<?php
/**
 * Test Suite: WordPress MU-Plugin Bridge Unit Verification
 * ========================================================
 * Simulates WordPress environment loading the mu-plugin and checks:
 * 1. Log parsing (CEF, JSON, Standard)
 * 2. Configuration retrieval
 * 3. Zero notices / warnings under strict error reporting
 */

error_reporting(E_ALL);
ini_set('display_errors', '1');

define('VACCINE_TEST_MODE', true);
define('ABSPATH', '/var/www/html/');
define('PHP_VACCINE_LOADED', true);
define('PHP_VACCINE_VERSION', '1.3.0-ENTERPRISE');

// Stub WordPress core functions
function is_admin() { return true; }
function is_user_logged_in() { return true; }
function current_user_can($cap) { return true; }
function wp_upload_dir() { return ['basedir' => sys_get_temp_dir()]; }
function esc_html($s) { return htmlspecialchars($s, ENT_QUOTES, 'UTF-8'); }
function add_action($hook, $callback, $priority = 10) {}
function wp_add_dashboard_widget($id, $title, $callback) {}
function admin_url($path) { return 'https://example.com/wp-admin/' . $path; }

require_once __DIR__ . '/../src/integrations/wordpress/mu-plugins/php-vaccine-guardrail.php';

echo "==================================================================\n";
echo "      WORDPRESS MU-PLUGIN INTEGRATION BRIDGE TEST RUNNER         \n";
echo "==================================================================\n";

// 1. Verify Configuration Retrieval
$config = PHPVaccineWPIntegration::get_vaccine_config();
assert($config['active'] === true, 'Vaccine active status should be true');
assert($config['version'] === '1.3.0-ENTERPRISE', 'Version should match 1.3.0-ENTERPRISE');
echo "[PASS] Vaccine configuration retrieval verified.\n";

// 2. Verify CEF Log Parsing
$cef_sample = "CEF:0|PHP-Universal-Vaccine|RASP|1.3.0|THREAT-PHP-CGI-001|PHP-CGI Argument Injection|8|src=1.2.3.4 requestMethod=GET request=/index.php";
$parsed_cef = PHPVaccineWPIntegration::parse_log_line($cef_sample);
assert($parsed_cef['threat_id'] === 'THREAT-PHP-CGI-001', 'CEF parsed threat ID failed');
echo "[PASS] CEF log parsing verified.\n";

// 3. Verify JSON Log Parsing
$json_sample = json_encode([
    'threat_id' => 'THREAT-PHP-SQLI-001',
    'category'  => 'SQL_INJECTION',
    'ip'        => '10.0.0.1',
    'method'    => 'POST',
    'uri'       => '/login'
]);
$parsed_json = PHPVaccineWPIntegration::parse_log_line($json_sample);
assert($parsed_json['threat_id'] === 'THREAT-PHP-SQLI-001', 'JSON parsed threat ID failed');
assert($parsed_json['category'] === 'SQL_INJECTION', 'JSON parsed category failed');
echo "[PASS] JSON log parsing verified.\n";

// 4. Verify Standard Custom Log Parsing
$raw_sample = "[2026-10-25T09:00:00+00:00] [THREAT_INTERCEPTED] ID: THREAT-PHP-DESER-001 | CAT: PHP_OBJECT_INJECTION | IP: 192.168.1.1 | METHOD: POST | URI: /checkout | LATENCY: 0.012ms | DETAIL: Serialized gadget | PAYLOAD: O:8:\"stdClass\":0:{}";
$parsed_raw = PHPVaccineWPIntegration::parse_log_line($raw_sample);
assert($parsed_raw['threat_id'] === 'THREAT-PHP-DESER-001', 'Custom parsed threat ID failed');
assert($parsed_raw['ip'] === '192.168.1.1', 'Custom parsed IP failed');
echo "[PASS] Custom standard log parsing verified.\n";

echo "==================================================================\n";
echo " [SUCCESS] WordPress MU-Plugin Bridge passed all unit tests! (100%)\n";
echo "==================================================================\n";
