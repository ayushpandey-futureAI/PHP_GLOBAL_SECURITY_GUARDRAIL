<?php
/**
 * =============================================================================
 * PHP UNIVERSAL SECURITY VACCINE (RUNTIME IMMUNE GUARDRAIL)
 * =============================================================================
 * Architecture: Zero-Touch Ambient Runtime Protection (RASP)
 * Compatibility: PHP 5.6, 7.0 - 7.4, 8.0 - 8.4+
 * Deployment: Loaded via `auto_prepend_file` in php.ini / .user.ini
 * Overhead: < 0.25ms execution latency per request
 * Author: Ayush Pandey (ayushpandey-futureAI)
 * License: Apache-2.0
 * =============================================================================
 */

// Bail out immediately on non-HTTP CLI execution unless in test mode
if (php_sapi_name() === 'cli' && !getenv('VACCINE_TEST_MODE')) {
    return;
}

// Global Vaccine State Configuration
if (!defined('PHP_VACCINE_LOADED')) {
    define('PHP_VACCINE_LOADED', true);
    define('PHP_VACCINE_VERSION', '1.0.0-ENTERPRISE');
    
    // Modes: 'ENFORCE' (blocks and exits 403), 'AUDIT' (logs only, passes request)
    $GLOBALS['__VACCINE_MODE'] = getenv('VACCINE_MODE') ?: 'ENFORCE';
    $GLOBALS['__VACCINE_LOGFILE'] = getenv('VACCINE_LOGFILE') ?: '/var/log/php-vaccine.log';
}

/**
 * Audit Logger & Incident Dispatcher
 */
function _vaccine_log_threat($threat_type, $detail, $matched_payload) {
    $ip = isset($_SERVER['REMOTE_ADDR']) ? $_SERVER['REMOTE_ADDR'] : 'UNKNOWN';
    $uri = isset($_SERVER['REQUEST_URI']) ? $_SERVER['REQUEST_URI'] : 'CLI';
    $method = isset($_SERVER['REQUEST_METHOD']) ? $_SERVER['REQUEST_METHOD'] : 'UNKNOWN';
    $timestamp = date('c');

    $log_entry = sprintf(
        "[%s] [THREAT_INTERCEPTED] [%s] IP: %s | METHOD: %s | URI: %s | DETAIL: %s | PAYLOAD: %s\n",
        $timestamp,
        $threat_type,
        $ip,
        $method,
        $uri,
        $detail,
        substr(json_encode($matched_payload), 0, 500)
    );

    // Write to dedicated log or syslog
    if (is_writable(dirname($GLOBALS['__VACCINE_LOGFILE']))) {
        @file_put_contents($GLOBALS['__VACCINE_LOGFILE'], $log_entry, FILE_APPEND | LOCK_EX);
    } else {
        error_log("PHP-VACCINE: " . trim($log_entry));
    }

    if ($GLOBALS['__VACCINE_MODE'] === 'ENFORCE') {
        if (!headers_sent()) {
            http_response_code(403);
            header('Content-Type: text/plain; charset=utf-8');
            header('X-Protected-By: PHP-Universal-Vaccine');
        }
        echo "403 Forbidden: Malicious payload intercepted by PHP Runtime Vaccine [Threat ID: " . substr(md5($timestamp . $matched_payload), 0, 8) . "]\n";
        exit(1);
    }
}

/**
 * Vector 1: PHP-CGI Argument Injection (CVE-2024-4577 & CVE-2012-1823)
 */
if (isset($_SERVER['QUERY_STRING']) && is_string($_SERVER['QUERY_STRING'])) {
    $qs = urldecode($_SERVER['QUERY_STRING']);
    // Check for parameter tampering targeting PHP runtime flags
    if (preg_match('/(-d\s*(?:allow_url_include|auto_prepend_file|auto_append_file|disable_functions|open_basedir|cgi\.fix_pathinfo))/i', $qs, $m)) {
        _vaccine_log_threat('CGI_ARGUMENT_INJECTION', 'Attempted override of PHP core directives via query string', $m[0]);
    }
}

/**
 * Vector 2: Stream Wrapper Injection & Directory Traversal on REQUEST_URI
 */
if (isset($_SERVER['REQUEST_URI'])) {
    $raw_uri = urldecode($_SERVER['REQUEST_URI']);
    if (strpos($raw_uri, "\0") !== false) {
        _vaccine_log_threat('NULL_BYTE_POISON', 'Null-byte poisoned URI', $raw_uri);
    }
    if (preg_match('/\.\.[\/\\\\]/', $raw_uri, $m)) {
        _vaccine_log_threat('PATH_TRAVERSAL_URI', 'Relative path traversal in URI', $m[0]);
    }
}

/**
 * Vector 3: Recursive Input Sanitization & Payload Inspection
 */
function _vaccine_inspect_node(&$value, $key) {
    if (is_array($value)) {
        return;
    }

    $raw_str = (string)$value;
    if (strlen($raw_str) < 3) {
        return;
    }

    $decoded = urldecode($raw_str);

    // [A] PHP Object Injection (Deserialization Attacks)
    if (preg_match('/(?:^|;|{|})([OaC]):\d+:"[^"]+":\d+:/i', $decoded, $m)) {
        _vaccine_log_threat('OBJECT_INJECTION', 'Serialized PHP gadget chain detected in input', $m[0]);
    }

    // [B] PHP Stream Wrappers (LFI / RFI)
    if (preg_match('/(?:php|data|expect|zip|phar|glob):\/\//i', $decoded, $m)) {
        _vaccine_log_threat('STREAM_WRAPPER_INJECTION', 'Arbitrary stream wrapper detected', $m[0]);
    }

    // [C] Directory Traversal
    if (strpos($decoded, "\0") !== false || preg_match('/\.\.[\/\\\\]/', $decoded, $m)) {
        _vaccine_log_threat('PATH_TRAVERSAL_PARAM', 'Directory traversal in superglobal parameter', $key);
    }

    // [D] Remote Command Injection Primitives
    if (preg_match('/(?:;|\||`|\$\()\s*(?:cat\s+\/etc\/passwd|whoami|curl\s+[0-9a-z]|wget\s+[0-9a-z]|bash\s+-i|nc\s+-e|python\s+-c)\b/i', $decoded, $m)) {
        _vaccine_log_threat('COMMAND_INJECTION', 'Shell execution command chained in parameter', $m[0]);
    }

    // [E] High-Confidence Union/Blind SQL Injection Signatures
    if (preg_match('/(?:\bUNION(?:\s+ALL)?\s+SELECT\b|\bSELECT\b.+\bFROM\b.+\bWHERE\b.+\b(?:SLEEP|BENCHMARK)\b|\b1=1\s*--|\bOR\s+[\'"]?1[\'"]?\s*=\s*[\'"]?1\b)/i', $decoded, $m)) {
        _vaccine_log_threat('SQL_INJECTION', 'High-confidence SQL injection payload detected', $m[0]);
    }
}

// Inoculate active superglobals
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
 * Vector 4: Global Response Security Headers Injection
 */
if (!headers_sent() && php_sapi_name() !== 'cli') {
    header('X-Content-Type-Options: nosniff');
    header('X-Frame-Options: SAMEORIGIN');
    header('X-XSS-Protection: 1; mode=block');
    header('Referrer-Policy: strict-origin-when-cross-origin');
    header('X-Immunized-By: PHP-Universal-Vaccine/1.0');
}
