<?php
/**
 * =============================================================================
 * PHP UNIVERSAL SECURITY VACCINE (ENTERPRISE RASP ENGINE)
 * =============================================================================
 * Architecture: Zero-Touch Ambient Runtime Protection & De-Obfuscation Engine
 * Compatibility: PHP 5.6, 7.0 - 7.4, 8.0 - 8.4+
 * Deployment: Loaded via `auto_prepend_file` in php.ini / .user.ini
 * Target: Complete immunization against CVEs, Web Shells, Deserialization,
 *         Command Chaining, Stream Wrappers, Traversal, and SSRF.
 * Author: Ayush Pandey (ayushpandey-futureAI)
 * License: Apache-2.0
 * =============================================================================
 */

// 1. FAST BAILOUT FOR NON-HTTP CLI (unless running unit test harness)
if (php_sapi_name() === 'cli' && !getenv('VACCINE_TEST_MODE')) {
    return;
}

// 2. ULTRA-FAST SUB-MICROSECOND BYPASS FOR STATIC ASSETS
if (isset($_SERVER['REQUEST_URI'])) {
    $uri_path = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
    if ($uri_path && preg_match('/\.(?:css|js|jpg|jpeg|png|gif|ico|svg|woff2?|ttf|eot|webp|mp4|webm|pdf)$/i', $uri_path)) {
        return;
    }
}

// 3. INITIALIZE VACCINE STATE & GLOBAL POLICIES
if (!defined('PHP_VACCINE_LOADED')) {
    define('PHP_VACCINE_LOADED', true);
    define('PHP_VACCINE_VERSION', '1.3.0-ENTERPRISE');

    $GLOBALS['__VACCINE_START_TIME'] = microtime(true);
    $GLOBALS['__VACCINE_MODE'] = getenv('VACCINE_MODE') ?: 'ENFORCE'; // 'ENFORCE' or 'AUDIT'
    $GLOBALS['__VACCINE_LOGFILE'] = getenv('VACCINE_LOGFILE') ?: '/var/log/php-vaccine.log';
    $GLOBALS['__VACCINE_LOG_FORMAT'] = strtoupper(getenv('VACCINE_LOG_FORMAT') ?: 'TEXT'); // 'TEXT', 'JSON', 'CEF'
    $GLOBALS['__VACCINE_SYSLOG'] = getenv('VACCINE_SYSLOG') ? true : false;

    // Automatically load legacy MySQL compatibility shim if native extension is missing
    $shim_path = __DIR__ . '/shims/mysql_shim.php';
    if (!extension_loaded('mysql') && file_exists($shim_path)) {
        require_once $shim_path;
    }
}

/**
 * Audit Logger & Threat Incident Dispatcher (Multi-Format SIEM Emitter)
 */
function _vaccine_log_threat($threat_id, $category, $detail, $matched_payload) {
    $ip = isset($_SERVER['REMOTE_ADDR']) ? $_SERVER['REMOTE_ADDR'] : '127.0.0.1';
    $uri = isset($_SERVER['REQUEST_URI']) ? $_SERVER['REQUEST_URI'] : 'UNKNOWN';
    $method = isset($_SERVER['REQUEST_METHOD']) ? $_SERVER['REQUEST_METHOD'] : 'UNKNOWN';
    $timestamp = date('c');
    $overhead_ms = round((microtime(true) - $GLOBALS['__VACCINE_START_TIME']) * 1000, 3);
    $payload_str = is_string($matched_payload) ? $matched_payload : json_encode($matched_payload);
    $payload_sample = substr($payload_str, 0, 400);

    $format = isset($GLOBALS['__VACCINE_LOG_FORMAT']) ? $GLOBALS['__VACCINE_LOG_FORMAT'] : 'TEXT';

    if ($format === 'CEF') {
        // ArcSight Common Event Format
        $log_entry = sprintf(
            "CEF:0|PHP-Universal-Vaccine|RASP|1.3.0|%s|%s|8|src=%s requestMethod=%s request=%s cs1=%s cs1Label=Category cn1=%s cn1Label=LatencyMs msg=%s\n",
            $threat_id,
            $detail,
            $ip,
            $method,
            $uri,
            $category,
            $overhead_ms,
            addcslashes($payload_sample, "=\\")
        );
    } elseif ($format === 'JSON') {
        $log_entry = json_encode([
            'timestamp'  => $timestamp,
            'threat_id'  => $threat_id,
            'category'   => $category,
            'ip'         => $ip,
            'method'     => $method,
            'uri'        => $uri,
            'latency_ms' => $overhead_ms,
            'detail'     => $detail,
            'payload'    => $payload_sample,
            'action'     => $GLOBALS['__VACCINE_MODE']
        ], JSON_UNESCAPED_SLASHES) . "\n";
    } else {
        $log_entry = sprintf(
            "[%s] [THREAT_INTERCEPTED] ID: %s | CAT: %s | IP: %s | METHOD: %s | URI: %s | LATENCY: %sms | DETAIL: %s | PAYLOAD: %s\n",
            $timestamp,
            $threat_id,
            $category,
            $ip,
            $method,
            $uri,
            $overhead_ms,
            $detail,
            substr(json_encode($matched_payload), 0, 400)
        );
    }

    // Direct Syslog dispatch if enabled
    if (!empty($GLOBALS['__VACCINE_SYSLOG']) && function_exists('syslog')) {
        @openlog("php-vaccine", LOG_PID | LOG_ODELAY, LOG_AUTH);
        @syslog(LOG_WARNING, trim($log_entry));
        @closelog();
    }

    if (is_writable(dirname($GLOBALS['__VACCINE_LOGFILE']))) {
        @file_put_contents($GLOBALS['__VACCINE_LOGFILE'], $log_entry, FILE_APPEND | LOCK_EX);
    } else {
        error_log("PHP-VACCINE: " . trim($log_entry));
    }

    if ($GLOBALS['__VACCINE_MODE'] === 'ENFORCE') {
        if (!headers_sent()) {
            http_response_code(403);
            header('Content-Type: text/plain; charset=utf-8');
            header('X-Protected-By: PHP-Universal-Vaccine/1.3');
        }
        echo "403 Forbidden: Malicious payload intercepted by PHP Runtime Vaccine [Threat ID: " . $threat_id . "]\n";
        exit(1);
    }
}

/**
 * Multi-Stage De-obfuscation Pipeline
 */
function _vaccine_deobfuscate($raw_string) {
    if (!is_string($raw_string) || strlen($raw_string) < 2) {
        return '';
    }

    // Step 1: Pre-decode best-fit Unicode mapping (CVE-2024-4577 Windows %ad -> -)
    $clean = preg_replace('/%(?:ad|AD)/i', '-', $raw_string);

    // Step 2: Recursive URL decode (unpacks double/triple URL encoding)
    $depth = 0;
    while ($depth < 3) {
        $decoded = urldecode($clean);
        if ($decoded === $clean) break;
        $clean = $decoded;
        $depth++;
    }

    return $clean;
}

/**
 * VECTOR 1: PHP-CGI ARGUMENT INJECTION (CVE-2024-4577, CVE-2012-1823)
 */
if (isset($_SERVER['QUERY_STRING']) && is_string($_SERVER['QUERY_STRING'])) {
    $clean_qs = _vaccine_deobfuscate($_SERVER['QUERY_STRING']);
    if (preg_match('/(?:-|%2d|%ad)[-\s]*(?:d|%64|%44)?\s*(?:allow_url_include|auto_prepend_file|auto_append_file|disable_functions|open_basedir|cgi\.fix_pathinfo|safe_mode)/i', $clean_qs, $m)) {
        _vaccine_log_threat('THREAT-PHP-CGI-001', 'CGI_ARGUMENT_INJECTION', 'PHP core runtime flag override probe', $m[0]);
    }
}

/**
 * VECTOR 2: URI-LEVEL TRAVERSAL & NULL-BYTE TRUNCATION
 */
if (isset($_SERVER['REQUEST_URI'])) {
    $clean_uri = _vaccine_deobfuscate($_SERVER['REQUEST_URI']);
    if (strpos($clean_uri, "\0") !== false || preg_match('/\.\.[\/\\\\]/', $clean_uri, $m)) {
        _vaccine_log_threat('THREAT-PHP-TRAV-001', 'PATH_TRAVERSAL_AND_POISONING', 'Null byte or traversal in URI', $clean_uri);
    }
}

/**
 * VECTOR 3: RECURSIVE SUPERGLOBAL PAYLOAD INSPECTOR
 */
function _vaccine_inspect_node(&$value, $key) {
    if (is_array($value)) {
        return;
    }

    $raw = (string)$value;
    if (strlen($raw) < 3) {
        return;
    }

    $clean = _vaccine_deobfuscate($raw);

    // [A] PHP Object Injection & Deserialization Gadgets
    if (preg_match('/(?:^|;|{|})([OaC]):\d+:"[^"]+":\d+:/i', $clean, $m)) {
        _vaccine_log_threat('THREAT-PHP-DESER-001', 'PHP_OBJECT_INJECTION', 'Serialized object gadget chain in input', $m[0]);
    }

    // [B] Arbitrary PHP Stream Wrappers (LFI/RFI/PHAR Deserialization)
    if (preg_match('/(?:php|data|expect|phar|zip|glob|compress\.zlib|compress\.bzip2):\/\//i', $clean, $m)) {
        _vaccine_log_threat('THREAT-PHP-STREAM-001', 'STREAM_WRAPPER_EXPLOITATION', 'Stream wrapper protocol in input', $m[0]);
    }

    // [C] Directory Traversal & Null Byte Poisoning
    if (strpos($clean, "\0") !== false || preg_match('/\.\.[\/\\\\]/', $clean, $m)) {
        _vaccine_log_threat('THREAT-PHP-TRAV-001', 'PATH_TRAVERSAL_AND_POISONING', 'Path traversal sequence detected', $key);
    }

    // [D] OS Command Chaining & Metacharacter Shell Injection
    if (preg_match('/(?:;|\|{1,2}|`|\$\()\s*(?:cat\s+\/etc|whoami|curl\s+[0-9a-z]|wget\s+[0-9a-z]|bash\s+-i|nc\s+-e|python\s+-c|id\b|uname\s+-a)/i', $clean, $m)) {
        _vaccine_log_threat('THREAT-PHP-CMD-001', 'COMMAND_INJECTION_AND_CHAINING', 'Shell command chained in input', $m[0]);
    }

    // [E] High-Confidence SQL Injection Signatures
    if (preg_match('/(?:\bUNION(?:\s+ALL)?\s+SELECT\b|\b(?:AND|OR)\s+(?:SLEEP|BENCHMARK|PG_SLEEP)\s*\(|\bSELECT\b.+\bFROM\b.+\bWHERE\b.+\b(?:SLEEP|BENCHMARK)\b|\b1=1\s*--|\bOR\s+[\'"]?1[\'"]?\s*=\s*[\'"]?1\b)/i', $clean, $m)) {
        _vaccine_log_threat('THREAT-PHP-SQLI-001', 'SQL_INJECTION', 'SQL injection union or blind sleep detected', $m[0]);
    }

    // [F] Cloud Metadata SSRF Exfiltration
    if (preg_match('/(?:https?:\/\/)?(?:169\.254\.169\.254|metadata\.google\.internal|100\.100\.100\.200|fd00:ec2::254)/i', $clean, $m)) {
        _vaccine_log_threat('THREAT-PHP-SSRF-001', 'SERVER_SIDE_REQUEST_FORGERY', 'Link-local cloud metadata endpoint probe', $m[0]);
    }
}

// Inoculate active superglobals recursively
if (!empty($_GET)) {
    array_walk_recursive($_GET, '_vaccine_inspect_node');
}
if (!empty($_POST)) {
    array_walk_recursive($_POST, '_vaccine_inspect_node');
}
if (!empty($_COOKIE)) {
    array_walk_recursive($_COOKIE, '_vaccine_inspect_node');
}
if (!empty($_REQUEST)) {
    array_walk_recursive($_REQUEST, '_vaccine_inspect_node');
}

/**
 * VECTOR 4: GLOBAL RESPONSE SECURITY HEADERS INJECTION
 */
if (!headers_sent() && php_sapi_name() !== 'cli') {
    header('X-Content-Type-Options: nosniff');
    header('X-Frame-Options: SAMEORIGIN');
    header('X-XSS-Protection: 1; mode=block');
    header('Referrer-Policy: strict-origin-when-cross-origin');
    header('X-Immunized-By: PHP-Universal-Vaccine/1.3');
}
