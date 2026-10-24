<?php
/**
 * PHP UNIVERSAL VACCINE TEST SUITE
 * Simulates high-risk exploit payloads & validates benign traffic acceptance.
 */

$vaccine_path = dirname(__DIR__) . '/src/vaccine.php';
putenv('VACCINE_TEST_MODE=1');
putenv('VACCINE_MODE=ENFORCE');

$tests = [
    'CVE-2024-4577 (CGI Arg Injection)' => [
        'type' => 'QUERY',
        'input' => '-d allow_url_include=1',
        'expect_block' => true
    ],
    'CVE-2012-1823 (CGI Arg Injection)' => [
        'type' => 'QUERY',
        'input' => '-d auto_prepend_file=/etc/passwd',
        'expect_block' => true
    ],
    'PHP Object Injection (Gadget Chain)' => [
        'type' => 'GET',
        'key' => 'data',
        'input' => 'O:8:"stdClass":1:{s:4:"test";s:4:"hack";}',
        'expect_block' => true
    ],
    'Stream Wrapper (php://input)' => [
        'type' => 'GET',
        'key' => 'page',
        'input' => 'php://input',
        'expect_block' => true
    ],
    'Stream Wrapper (data:// wrapper)' => [
        'type' => 'POST',
        'key' => 'file',
        'input' => 'data://text/plain;base64,PD9waHAgc3lzdGVtKCRfR0VUWydjJ10pOyA/Pg==',
        'expect_block' => true
    ],
    'Path Traversal (../../etc/passwd)' => [
        'type' => 'GET',
        'key' => 'doc',
        'input' => '../../../../etc/passwd',
        'expect_block' => true
    ],
    'Command Chaining (cat /etc/passwd)' => [
        'type' => 'POST',
        'key' => 'ip',
        'input' => '127.0.0.1; cat /etc/passwd',
        'expect_block' => true
    ],
    'Command Chaining (whoami pipe)' => [
        'type' => 'GET',
        'key' => 'cmd',
        'input' => 'test || whoami',
        'expect_block' => true
    ],
    'High-Confidence SQLi (UNION SELECT)' => [
        'type' => 'GET',
        'key' => 'id',
        'input' => '-1 UNION SELECT 1, 2, version() --',
        'expect_block' => true
    ],
    'High-Confidence SQLi (Sleep Injection)' => [
        'type' => 'POST',
        'key' => 'search',
        'input' => 'SELECT * FROM users WHERE id=1 AND SLEEP(5)',
        'expect_block' => true
    ],
    'BENIGN: Normal User Search' => [
        'type' => 'GET',
        'key' => 'q',
        'input' => 'best high performance php frameworks 2026',
        'expect_block' => false
    ],
    'BENIGN: Normal JSON Payload' => [
        'type' => 'POST',
        'key' => 'payload',
        'input' => '{"user_id": 42, "role": "engineer", "status": "active"}',
        'expect_block' => false
    ],
    'BENIGN: Regular Contact Form Message' => [
        'type' => 'POST',
        'key' => 'message',
        'input' => 'Hello team, I would like to inquire about the enterprise consulting pricing.',
        'expect_block' => false
    ]
];

echo "=================================================================\n";
echo "       PHP UNIVERSAL VACCINE: EXPLOIT SIMULATION TEST RUNNER     \n";
echo "=================================================================\n";

$passed = 0;
$failed = 0;

foreach ($tests as $name => $spec) {
    // Run each in an isolated sub-process
    $cmd = 'php -r ' . escapeshellarg(sprintf('
        putenv("VACCINE_TEST_MODE=1");
        putenv("VACCINE_MODE=ENFORCE");
        putenv("VACCINE_LOGFILE=/tmp/php_vaccine_test.log");
        $_SERVER["REQUEST_URI"] = "/index.php";
        $_SERVER["REMOTE_ADDR"] = "127.0.0.1";
        $_SERVER["REQUEST_METHOD"] = "%s";
        
        if ("%s" === "QUERY") {
            $_SERVER["QUERY_STRING"] = %s;
        } elseif ("%s" === "GET") {
            $_GET[%s] = %s;
        } elseif ("%s" === "POST") {
            $_POST[%s] = %s;
        }
        
        require "%s";
        echo "SUCCESS_ALLOWED";
    ', 
        $spec['type'] === 'POST' ? 'POST' : 'GET',
        $spec['type'],
        json_encode($spec['input']),
        $spec['type'],
        json_encode(isset($spec['key']) ? $spec['key'] : ''),
        json_encode($spec['input']),
        $spec['type'],
        json_encode(isset($spec['key']) ? $spec['key'] : ''),
        json_encode($spec['input']),
        $vaccine_path
    ));

    $output = shell_exec($cmd . ' 2>&1');
    $was_blocked = (strpos($output, '403 Forbidden') !== false);
    
    $test_ok = false;
    if ($spec['expect_block'] && $was_blocked) {
        $test_ok = true;
    } elseif (!$spec['expect_block'] && !$was_blocked && strpos($output, 'SUCCESS_ALLOWED') !== false) {
        $test_ok = true;
    }

    if ($test_ok) {
        printf("  [PASS] %-42s => %s\n", $name, $was_blocked ? "BLOCKED (403)" : "ALLOWED (200)");
        $passed++;
    } else {
        printf("  [FAIL] %-42s => Expected: %s, Got: %s\n", 
            $name, 
            $spec['expect_block'] ? "BLOCKED" : "ALLOWED", 
            $was_blocked ? "BLOCKED" : "ALLOWED"
        );
        echo "         Output: " . trim($output) . "\n";
        $failed++;
    }
}

echo "=================================================================\n";
printf(" Test Summary: Total: %d | Passed: %d | Failed: %d\n", count($tests), $passed, $failed);
echo "=================================================================\n";

exit($failed > 0 ? 1 : 0);
