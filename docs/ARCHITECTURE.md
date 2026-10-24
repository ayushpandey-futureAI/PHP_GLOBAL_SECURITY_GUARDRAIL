# TECHNICAL SPECIFICATION: PHP GLOBAL SECURITY GUARDRAIL

## 1. System Overview
The PHP Universal Security Vaccine provides an in-memory application firewall utilizing PHP's native `auto_prepend_file` configuration directive. 

By loading before userland scripts are compiled by the Zend Engine, the vaccine acts as a first line of defense against parameter tampering, code execution primitives, and deserialization gadget chains.

## 2. Ingress & Lifecycle
1. **HTTP Ingress:** The web server (NGINX or Apache) accepts the incoming HTTP request.
2. **Directory Isolation:** NGINX rejects any request attempting to execute `.php` inside writable upload directories (`/uploads/`, `/wp-content/uploads/`) with `404 Not Found`.
3. **Engine Boot:** FastCGI passes the request to the PHP worker pool.
4. **Pre-Flight Inspection (`vaccine.php`):**
   - Query strings are evaluated for CGI argument flags.
   - Superglobals (`$_GET`, `$_POST`, `$_COOKIE`, `$_REQUEST`) are recursively scanned.
   - If an exploit signature matches, `_vaccine_log_threat()` triggers, emits HTTP 403, writes to `/var/log/php-vaccine.log`, and terminates the process (`exit(1)`).
5. **Security Header Injection:** Headers are added before any application output buffer begins.
6. **Application Execution:** Control transfers cleanly to the main application script (`index.php`).
