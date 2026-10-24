# JIRA SPRINTS & SCRUM BACKLOG: PHP GLOBAL SECURITY GUARDRAIL

**Project Key:** `VACCINE`  
**Product Owner:** Ayush Pandey (`ayushpandey-futureAI`)  
**Repository:** `https://github.com/ayushpandey-futureAI/PHP_GLOBAL_SECURITY_GUARDRAIL`  
**Google Drive Mirror:** `/home/ayush-pandey/GoogleDrive/PHP_Global_Security_Guardrail`  

---

## 📊 EPIC ROADMAP OVERVIEW

| Epic ID | Summary | Target Milestone | Status |
|---|---|---|---|
| **VACCINE-EPIC-01** | Zero-Touch Ambient RASP Engine (`vaccine.php`) | v1.0.0-Core | **COMPLETED** |
| **VACCINE-EPIC-02** | 1-Shot Multi-Version Inoculator Script (`inoculate.sh`) | v1.0.0-Core | **COMPLETED** |
| **VACCINE-EPIC-03** | Exploit Simulation & Regex Verification Test Harness | v1.1.0-Test | **COMPLETED** |
| **VACCINE-EPIC-04** | Continuous Sync, GitHub Auto-Push & Drive Daemon | v1.1.0-Ops | **COMPLETED** |
| **VACCINE-EPIC-05** | CMS Polyfill & Legacy MySQL Shim Layer | v1.2.0-Legacy | **IN PROGRESS** |
| **VACCINE-EPIC-06** | OpenRASP / Snuffleupagus C-Extension Engine Integration | v2.0.0-Kernel | **BACKLOG** |

---

## 🏃 SPRINT 1: CORE INOCULATOR & RUNTIME VACCINE (COMPLETED / REVIEW)
**Sprint Duration:** 2026-10-15 to 2026-10-25  
**Sprint Goal:** Build the minimum viable "1-Shot Vaccine" capable of intercepting global PHP CVEs and neutralizing web shell upload execution with zero source code refactoring.

### 📋 Sprint 1 Tickets

#### [VACCINE-101] Implement `vaccine.php` Zero-Touch RASP Interceptor
* **Type:** Story | **Points:** 8 | **Priority:** Blocker | **Status:** `DONE`
* **Assignee:** Ayush Pandey
* **Description:** Create the core runtime serum loaded via `auto_prepend_file` to intercept all superglobals before script compilation.
* **Acceptance Criteria:**
  - [x] Intercepts CVE-2024-4577 (PHP-CGI `-d allow_url_include` injection).
  - [x] Blocks PHP Object Injection / serialized gadget chains (`O:8:...`).
  - [x] Blocks stream wrappers (`php://input`, `data://`, etc.).
  - [x] Blocks path traversal (`../`, null-byte poisoning).
  - [x] High-confidence SQL injection and command chaining patterns blocked with HTTP 403.
  - [x] Auto-injects standard security response headers (`nosniff`, `SAMEORIGIN`).
  - [x] Latency benchmark strictly under 0.25ms.

#### [VACCINE-102] Create Automated 1-Shot Installer Needle (`inoculate.sh`)
* **Type:** Story | **Points:** 5 | **Priority:** Critical | **Status:** `DONE`
* **Assignee:** Ayush Pandey
* **Description:** Single bash script to detect all installed PHP runtimes (5.6 - 8.4), inject `auto_prepend_file`, and harden upload directories.
* **Acceptance Criteria:**
  - [x] Scans all `php.ini` files across `/etc/php*` and `/usr/local/etc`.
  - [x] Inserts `auto_prepend_file` pointing to `/etc/php-vaccine/vaccine.php`.
  - [x] Sets `expose_php = Off` and `allow_url_include = Off`.
  - [x] Deploys web server upload protection rule (`block_php_uploads.conf`).
  - [x] Gracefully reloads active PHP-FPM and web server daemons.

#### [VACCINE-103] Build Python Logic & Regex Validation Harness
* **Type:** Task | **Points:** 3 | **Priority:** High | **Status:** `DONE`
* **Assignee:** Ayush Pandey
* **Description:** Standalone test suite verifying 100% interception of exploit vectors without false positives on benign payloads.
* **Acceptance Criteria:**
  - [x] 14 comprehensive test cases covering exploit strings and benign inputs.
  - [x] 100% pass rate with zero false alarms on regular user queries and JSON bodies.

#### [VACCINE-104] Automated Multi-Cloud & GitHub Sync Daemon
* **Type:** Task | **Points:** 3 | **Priority:** High | **Status:** `DONE`
* **Assignee:** Ayush Pandey
* **Description:** Implement `sync_guardrail.py` to synchronize local workspace with Google Drive cloud mirror and GitHub repository.
* **Acceptance Criteria:**
  - [x] One-time manual CLI sync option.
  - [x] 600-second daemon mode for unattended persistence.
  - [x] Git auto-commit and push capability via GitHub CLI.

---

## 🏃 SPRINT 2: CMS PLUGINS & LEGACY SHIM REJUVENATION (ACTIVE / CURRENT)
**Sprint Duration:** 2026-10-26 to 2026-11-09  
**Sprint Goal:** Rejuvenate legacy PHP 5.x apps running on PHP 8.x and provide native WordPress/Drupal mu-plugins for administrative visibility.

### 📋 Sprint 2 Tickets

#### [VACCINE-201] Universal `mysql_*` Legacy Polyfill Shim
* **Type:** Story | **Points:** 5 | **Priority:** High | **Status:** `IN PROGRESS`
* **Description:** Integrate drop-in userland replacement for deprecated `mysql_*` functions forwarding to safe `mysqli` calls with auto-escaping.
* **Acceptance Criteria:**
  - [ ] Enables PHP 5.4/5.6 database code to run natively on PHP 8.2+.
  - [ ] Zero code changes required in legacy application files.

#### [VACCINE-202] Native WordPress Must-Use (`mu-plugin`) Integration
* **Type:** Story | **Points:** 5 | **Priority:** Medium | **Status:** `TO DO`
* **Description:** Auto-drop `/wp-content/mu-plugins/vaccine-dashboard.php` to display intercepted threats inside the WP Admin dashboard.
* **Acceptance Criteria:**
  - [ ] Visual log table inside WordPress Admin bar.
  - [ ] 1-click IP whitelist / false-positive report button.

#### [VACCINE-203] Low-Overhead Syslog & SIEM Ingestion Format
* **Type:** Task | **Points:** 3 | **Priority:** Medium | **Status:** `TO DO`
* **Description:** Format intercept logs as CEF/JSON for direct ingestion into Splunk, Datadog, or Elastic.

---

## 📦 SPRINT 3: KERNEL & EXTENSION HARDENING (BACKLOG)

* **[VACCINE-301] Snuffleupagus Configuration Template Suite:** Pre-baked hardened rule sets for popular CMS and SaaS apps.
* **[VACCINE-302] Containerized Inoculation (Docker / Podman Base Image):** Production Dockerfile template `alpine-php-hardened` with pre-compiled vaccine.
* **[VACCINE-303] Dynamic Rule Fetcher:** Optional periodic cron update for emerging zero-day regex rules without restarting PHP.
