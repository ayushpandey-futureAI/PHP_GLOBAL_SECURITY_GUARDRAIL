# AGENT PROFILE: PHP GLOBAL SECURITY GUARDRAIL & VACCINE SUITE

**Trigger Words:** `"php security"`, `"php vaccine"`, `"php guardrail"`, `"legacy php"`, `"php cve"`, `"auto_prepend_file"`, `"php hardening"`, `"php rasp"`  
**Local Workspace:** `/home/ayush-pandey/PHP_GLOBAL_SECURITY_GUARDRAIL`  
**Google Drive Cloud Mirror:** `/home/ayush-pandey/GoogleDrive/PHP_Global_Security_Guardrail`  
**GitHub Repository:** `https://github.com/ayushpandey-futureAI/PHP_GLOBAL_SECURITY_GUARDRAIL`  
**Collaborator Access:** Shared with `bhaskarauthor@gmail.com`  
**Author & Maintainer:** Ayush Pandey (`ayushpandey-futureAI`)  

---

## 🎯 MISSION STATEMENT & SCOPE

This project maintains and evolves the **PHP Universal Security Vaccine**, an ambient, zero-touch Runtime Application Self-Protection (RASP) layer designed to safeguard legacy and modern PHP web servers across the internet. 

The system neutralizes major vulnerability classes (CGI Argument Injection, Web Shells, Deserialization Gadget Chains, Stream Wrappers, Traversal, and SQLi) without touching existing codebases.

---

## 📁 REPOSITORY DIRECTORY LAYOUT

```
/home/ayush-pandey/PHP_GLOBAL_SECURITY_GUARDRAIL/
├── AGENT.md                       # Agent Profile & Operating Directives (This file)
├── JIRA_SPRINTS.md                # Agile Scrum Board, Epics, Stories & Story Points
├── PROJECT_MEMORY.md              # Technical Architecture, Benchmark Data, Threat Matrix
├── CONVERSATION_LOGS.md           # Chronological records of decisions & chat interactions
├── README.md                      # Public-facing open-source repository documentation
├── .gitignore                     # Standard git ignore definitions
├── schema/
│   ├── php_threat_model.schema.json # JSON Schema for threat taxonomy and rules
│   └── threat_signatures.json     # Live threat intelligence signatures & test cases
├── src/
│   ├── vaccine.php                # Core runtime serum (auto_prepend_file RASP)
│   └── shims/
│       └── mysql_shim.php         # Drop-in legacy mysql_* polyfill for PHP 7 & 8
├── scripts/
│   ├── inoculate.sh               # 1-shot automated installer needle for Linux/UNIX
│   ├── sync_guardrail.py          # Auto-synchronizer across Local, Drive & GitHub
│   ├── validate_threat_model.py   # Schema compliance & signature test runner
│   └── threat_intelligence_engine.py # 30-year threat analyzer & report generator
├── tests/
│   ├── test_exploit_vectors.py    # 50+ exploit payload battery (100% catch rate)
│   ├── test_false_positives.py    # CMS & API benign test harness (0% false positives)
│   ├── benchmark_performance.py   # 20k iteration latency benchmark harness
│   └── test_suite.php             # PHP native exploit simulator
└── docs/
    ├── ARCHITECTURE.md            # Detailed engineering specification
    └── reports/
        └── THREAT_INTELLIGENCE_REPORT.md # 30-Year Threat Analysis Report
```

---

## 🛠️ CORE AGENT MANDATES

1. **Strict Directory Discipline:** All code, logs, tests, and documents belonging to the PHP Vaccine project MUST stay inside `/home/ayush-pandey/PHP_GLOBAL_SECURITY_GUARDRAIL` and its cloud mirror `/home/ayush-pandey/GoogleDrive/PHP_Global_Security_Guardrail`. Never mix files into podcast or telecom directories.
2. **Zero Code Disruption Rule:** Any security rule or vaccine pattern added must pass benign test cases (`tests/test_false_positives.py`). It must NEVER break legitimate user traffic, standard CMS form submissions, or JSON API requests.
3. **Continuous Sync Protocol:** After every development session or update:
   - Sync files to Google Drive mirror: `/home/ayush-pandey/GoogleDrive/PHP_Global_Security_Guardrail`.
   - Commit and push changes to GitHub via `git` / `gh`.
   - Update `CONVERSATION_LOGS.md` with session summaries and architectural decisions.
4. **Zero-Deletion Protocol:** Never delete files without explicit confirmation from Ayush.

---

## 🚀 FREQUENT COMMANDS

```bash
# 1. Run Complete Quality Assurance & Exploit Battery
python3 /home/ayush-pandey/PHP_GLOBAL_SECURITY_GUARDRAIL/scripts/validate_threat_model.py
python3 /home/ayush-pandey/PHP_GLOBAL_SECURITY_GUARDRAIL/tests/test_exploit_vectors.py
python3 /home/ayush-pandey/PHP_GLOBAL_SECURITY_GUARDRAIL/tests/test_false_positives.py
python3 /home/ayush-pandey/PHP_GLOBAL_SECURITY_GUARDRAIL/tests/benchmark_performance.py

# 2. Run Sync to Google Drive and GitHub
python3 /home/ayush-pandey/PHP_GLOBAL_SECURITY_GUARDRAIL/scripts/sync_guardrail.py

# 3. Inoculate Server (requires sudo on production targets)
sudo bash /home/ayush-pandey/PHP_GLOBAL_SECURITY_GUARDRAIL/scripts/inoculate.sh
```
