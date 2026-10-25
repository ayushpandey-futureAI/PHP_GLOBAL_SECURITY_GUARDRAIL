# Contributing to PHP Universal Security Vaccine & Guardrail

Thank you for your interest in contributing to the **PHP Universal Security Vaccine**! Together, we are safeguarding hundreds of millions of legacy and modern web applications across the global internet.

---

## 🏛️ Guiding Principles

1. **Zero Source Code Refactoring:** The core vaccine MUST execute ambiently via `auto_prepend_file` without modifying userland applications.
2. **Sub-Microsecond Latency Budget:** All regex inspections, normalization loops, and de-obfuscation routines must evaluate in **< 25 µs (0.025 ms)** per request.
3. **Zero False-Positive Mandate:** Any new threat rule must pass the entire benign test suite (`tests/test_false_positives.py`). We never break legitimate user traffic, WordPress Gutenberg blocks, WooCommerce form posts, or base64 images.
4. **Deterministic Declarative Schema:** All threat definitions must reside in `schema/threat_signatures.json` with CVSS v4.0 and EPSS scoring.

---

## 🛠️ Development Setup & Workflow

1. **Fork and Clone:**
   ```bash
   git clone https://github.com/ayushpandey-futureAI/PHP_GLOBAL_SECURITY_GUARDRAIL.git
   cd PHP_GLOBAL_SECURITY_GUARDRAIL
   ```

2. **Verify Test Harness:**
   Before making any changes, ensure all 14 test suites pass:
   ```bash
   python3 scripts/validate_threat_model.py
   python3 tests/test_exploit_vectors.py
   python3 tests/test_false_positives.py
   python3 tests/test_siem_logging.py
   python3 tests/test_wordpress_mu_plugin_bridge.py
   python3 tests/benchmark_performance.py
   ```

---

## 🛡️ Adding a New Threat Signature

1. Update `schema/threat_signatures.json` complying with `schema/php_threat_model.schema.json`.
2. Provide at least two exploit test fixtures and two benign fixtures.
3. Run `python3 scripts/threat_intelligence/cve_synthesizer.py` to assert regex safety against catastrophic backtracking (ReDoS).
4. Run `python3 scripts/threat_intelligence/epss_calibrator.py` to calibrate enforcement policies.
5. Add the regex rule to `src/vaccine.php`.
6. Run `python3 tests/test_exploit_vectors.py` and `python3 tests/test_false_positives.py` to confirm 100% catch rate and 0% false positives.

---

## 📦 Pull Request Guidelines

* Create a feature branch: `git checkout -b feat/my-security-rule`.
* Ensure commits follow conventional commit standards (`feat:`, `fix:`, `docs:`, `test:`).
* All tests in GitHub Actions CI must pass before merging.
