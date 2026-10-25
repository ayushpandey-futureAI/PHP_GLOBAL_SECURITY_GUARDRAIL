# 🛠️ TECHNICAL ARCHITECTURE & DEEP ENGINEERING SPECIFICATION

**Document Version:** 2.0.0  
**Target:** Global PHP Ecosystem Ambient Protection  
**Classification:** Core Engineering Standard  
**Maintainer:** Ayush Pandey (`ayushpandey-futureAI`)  
**Repository:** `https://github.com/ayushpandey-futureAI/PHP_GLOBAL_SECURITY_GUARDRAIL`  

---

## 🏗️ SYSTEM ARCHITECTURE OVERVIEW

The **PHP Universal Security Guardrail** implements a multi-tier defense-in-depth model that protects web applications across all execution phases—from network ingress to Zend Engine opcode evaluation.

```
                          INCOMING HTTP REQUEST
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ SECTION 1: INGRESS & WEB SERVER ISOLATION (NGINX / Apache)             │
│ • Direct denial of script execution in upload directories (404/403)    │
│ • Rejection of dotfiles (.env, .git)                                   │
│ • Reverse-proxy buffer sanitization                                    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ FastCGI Socket (php-fpm:9000)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ SECTION 2: AMBIENT RUNTIME RASP SERUM (src/vaccine.php)                │
│ • Loaded via auto_prepend_file before script compilation               │
│ • Multi-Stage De-obfuscation Pipeline (Unicode normalization, URL-dec) │
│ • Superglobal Threat Filter (CGI flags, Deserialization, SSRF, SQLi)   │
│ • Header Injection (X-Content-Type-Options, X-Frame-Options)           │
└──────────────────┬─────────────────────────────────┬───────────────────┘
                   │ Malicious                       │ Clean
                   ▼                                 ▼
┌──────────────────────────────────────┐  ┌──────────────────────────────┐
│ SECTION 7: SIEM DISPATCH & TELEMETRY │  │ SECTION 3: ZEND HARDENING    │
│ • ArcSight CEF Standard              │  │ • Snuffleupagus C-Extension  │
│ • Structured JSON                    │  │ • Disarm eval(), exec()      │
│ • Direct Syslog Socket Streaming     │  │ • Block gadget chain entry   │
│ • HTTP 403 Active Drop               │  └──────────────┬───────────────┘
└──────────────────────────────────────┘                 │
                                                         ▼
                                          ┌──────────────────────────────┐
                                          │ SECTION 4: LEGACY SHIMS      │
                                          │ • mysql_* to mysqli Wrapper  │
                                          │ • Auto-escaping & safe types │
                                          └──────────────┬───────────────┘
                                                         │
                                                         ▼
                                          ┌──────────────────────────────┐
                                          │ SECTION 5: CMS INTEGRATION   │
                                          │ • WordPress MU-Plugin Widget │
                                          │ • Admin bar live telemetry   │
                                          │ • Application Execution      │
                                          └──────────────────────────────┘
```

---

## SECTION 1: INGRESS & WEB SERVER HARDENING

### 1.1 Upload Execution Denial
Web shells and backdoor scripts (e.g. `c99`, `r57`, WSO) uploaded through compromised admin panels or CMS file-manager vulnerabilities are disarmed at the web server layer before reaching the PHP-FPM process pool.

* **NGINX Directive:**
  ```nginx
  location ~* /(?:uploads|files|wp-content/uploads|media|storage)/.*\.php$ {
      deny all;
      return 404;
  }
  ```
* **Apache Directive (`.htaccess` / VirtualHost):**
  ```apache
  <Directory "/var/www/*/wp-content/uploads">
      <FilesMatch "\.(php|phtml|php3|php4|php5|php7|php8|phar)$">
          Require all denied
      </FilesMatch>
  </Directory>
  ```

---

## SECTION 2: AMBIENT RUNTIME RASP SERUM (`src/vaccine.php`)

### 2.1 Execution Lifecycle & Ingress Hook
The serum is activated through the native PHP configuration directive:
```ini
auto_prepend_file = /etc/php-vaccine/vaccine.php
```
This forces the Zend Engine to compile and evaluate `vaccine.php` before any userland application code (e.g., WordPress `index.php`, Drupal `index.php`, Laravel `public/index.php`) is parsed.

### 2.2 Sub-Microsecond Static Asset Bypass
To eliminate overhead on static asset requests routed through PHP:
```php
if (isset($_SERVER['REQUEST_URI'])) {
    $uri_path = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
    if ($uri_path && preg_match('/\.(?:css|js|jpg|jpeg|png|gif|ico|svg|woff2?|ttf|eot|webp|mp4|webm|pdf)$/i', $uri_path)) {
        return;
    }
}
```

### 2.3 Multi-Stage De-Obfuscation Pipeline
Attackers frequently disguise payloads using non-standard encodings, Windows best-fit characters, or multi-nested URL encoding. The engine implements a recursive de-obfuscation pipeline:
1. **Windows Best-Fit Unicode Normalization:** Converts `%ad` and `%AD` soft-hyphens into standard ASCII hyphens (`-`).
2. **Recursive URL Decode:** Decodes up to 3 layers of URL percent-encoding to counter double-encoding evasion.
3. **Null-Byte Normalization:** Detects raw null characters (`\0`) and percent-encoded `%00`.

### 2.4 Threat Interception Vector Matrix
* **CGI Parameter Injection (CVE-2024-4577, CVE-2012-1823):**
  Inspects `$_SERVER['QUERY_STRING']` and `REQUEST_URI` for runtime configuration flags:
  `/(?:-|%2d|%ad)[-\s]*(?:d|%64|%44)?\s*(?:allow_url_include|auto_prepend_file|auto_append_file|disable_functions|open_basedir|cgi\.fix_pathinfo|safe_mode)/i`
* **Insecure Deserialization & PHPGGC Gadget Chains:**
  Detects serialized object headers matching `O:\d+:"`, `a:\d+:{`, `C:\d+:"` in superglobals and cookies.
* **Stream Wrapper Exploitation (LFI/RFI/PHAR):**
  Neutralizes pseudo-protocols: `php://`, `data://`, `expect://`, `phar://`, `zip://`, `glob://`.
* **Path Traversal & Truncation:**
  Detects `../`, `..\`, `%2e%2e`, and null-bytes in URI strings and request parameters.
* **Chained Command Injection:**
  Detects shell chaining operators (`;`, `|`, `||`, `` ` ``, `$()`) paired with system binaries (`cat /etc`, `whoami`, `curl`, `wget`, `nc`, `uname`).
* **High-Confidence SQL Injection:**
  Detects UNION SELECT queries, time-based blind timing attacks (`SLEEP()`, `BENCHMARK()`), and tautologies (`1=1 --`).
* **Cloud Metadata SSRF Protection:**
  Intercepts link-local cloud metadata queries (`169.254.169.254`, `metadata.google.internal`, `100.100.100.200`).

---

## SECTION 3: C-LEVEL ZEND ENGINE HARDENING (SNUFFLEUPAGUS)

Located in `config/snuffleupagus/`, rulesets hook into PHP's C-extension internals:
* **Function Disabling:** Completely disarms `dl()`, `create_function()`, and arbitrary `eval()`.
* **Process Execution Controls:** Restricts `system()`, `shell_exec()`, `passthru()`, `proc_open()`.
* **Class Deserialization Allowlisting:** Restricts `unserialize()` by dropping execution when known gadget chain entry classes (Monolog, GuzzleHttp, Illuminate, Symfony) are identified.

---

## SECTION 4: LEGACY REJUVENATION & DATABASE SHIMS (`src/shims/`)

### 4.1 Drop-In `mysql_*` Polyfill (`mysql_shim.php`)
Modern PHP versions (PHP 7.0+) removed the legacy `mysql_*` extension, breaking millions of older enterprise applications.
* The shim creates drop-in procedural replacements: `mysql_connect()`, `mysql_query()`, `mysql_fetch_assoc()`, `mysql_real_escape_string()`.
* Transparently maps calls to secure `mysqli` instances with auto-escaping.
* Allows PHP 4/5 database code to run with **zero code modifications on PHP 8.2+**.

---

## SECTION 5: CMS NATIVE INTEGRATIONS (`src/integrations/`)

### 5.1 WordPress Must-Use Integration (`mu-plugins/php-vaccine-guardrail.php`)
* **Zero-Touch Execution:** Loaded automatically from `/wp-content/mu-plugins/` before any theme or standard plugin loads.
* **Admin Bar Badge:** Displays real-time operational status (Active / Inactive) and mode.
* **Dashboard Widget:** Displays real-time incident feed parsed from `/var/log/php-vaccine.log`.
* **Multi-Format Parser:** Automatically handles CEF, JSON, and standard custom log lines.

---

## SECTION 6: DECLARATIVE THREAT MODEL SCHEMA (`schema/`)

* **Compliance:** Formulated using **JSON Schema Draft 2020-12** (`php_threat_model.schema.json`).
* **Live Taxonomy Database (`threat_signatures.json`):**
  - Catalogs 7 core threat categories with CVSS v4.0 scores, CWE IDs, and EPSS percentiles.
  - Contains 46 built-in test fixtures for automated validation via `scripts/validate_threat_model.py`.

---

## SECTION 7: ENTERPRISE OBSERVABILITY & SIEM DISPATCH

Configured via `VACCINE_LOG_FORMAT`:
* **ArcSight CEF Format:**
  ```
  CEF:0|PHP-Universal-Vaccine|RASP|1.3.0|THREAT-PHP-CGI-001|PHP-CGI Argument Injection probe|8|src=1.2.3.4 requestMethod=GET request=/index.php cs1=CGI_ARGUMENT_INJECTION cs1Label=Category cn1=0.015 cn1Label=LatencyMs msg=-d allow_url_include=1
  ```
* **Structured JSON Format:**
  Emits one-line JSON documents containing ISO-8601 timestamps, threat IDs, request metadata, and latency.
* **Kernel Syslog Streaming:**
  When `VACCINE_SYSLOG=1`, calls PHP's native `syslog(LOG_WARNING)` for non-blocking in-memory log transmission.

---

## SECTION 8: TURNKEY CONTAINERIZATION (`docker/`)

* **`Dockerfile.inoculated`:**
  Hardened multi-stage Alpine Linux base image with PHP 8.2-FPM, pre-installed vaccine serum, legacy shims, and hardened `php.ini`.
* **`nginx.conf`:**
  Reverse-proxy with pre-configured upload lockdown rules and security headers.
* **`docker-compose.yml`:**
  Single-command development and testing stack orchestrating NGINX, PHP-FPM, and MariaDB.
