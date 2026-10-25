# SOC 2 TYPE II SECURITY CONTROL EVIDENCE

**Audit Criteria:** Trust Services Criteria CC6.6 & CC6.7  
**Scope:** Boundary Protection & Prevention of Unauthorized Code Execution  
**Generated At:** 2026-10-25 04:58:00 UTC  
**Attestation Status:** **VERIFIED EFFECTIVE**  

---

## 1. CONTROL IMPLEMENTATION SUMMARY

* **CC6.6 (Boundary Protection):** The web server drops `.php` script execution in user-writable media directories (`/uploads/`) with HTTP 404, preventing web shell backdoors from running.
* **CC6.7 (Code Execution Prevention):** Opcode-level Zend engine hooks and RASP superglobal inspection neutralize PHP Object Injection gadget chains prior to compilation.

## 2. REPOSITORY HASH PROOF
* `src/vaccine.php`: `65aa31b61c815f93314898df7d22be12175a3fb862c4f1b8a10045d7c077a0b7`
* `src/shims/mysql_shim.php`: `cf4db5c2eec2aba9cd066fe41ad7c130adb6fc45dd282684b13c54e3f12058bf`
* `tests/test_false_positives.py`: `17215578e3dd2b8da6b6191d7735116029468f6987ecf2ebd48eec9bf1d7e732`
