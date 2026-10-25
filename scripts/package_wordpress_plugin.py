#!/usr/bin/env python3
"""
WordPress Plugin Distributable Packager
======================================
Builds the standalone, zero-touch WordPress distributable ZIP archive
ready for 1-click installation via WordPress Admin or WordPress.org SVN.
"""

import os
import zipfile
import hashlib
from pathlib import Path

ROOT = Path(__file__).parent.parent
DIST_DIR = ROOT / "dist"
VERSION = "1.3.0"
ZIP_NAME = f"php-vaccine-guardrail-v{VERSION}.zip"

def build_wordpress_zip():
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    zip_path = DIST_DIR / ZIP_NAME

    print(f"[*] Packaging WordPress Distributable: {zip_path}")

    # Build zip file structure
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        # 1. Main plugin bootstrap
        mu_file = ROOT / "src" / "integrations" / "wordpress" / "mu-plugins" / "php-vaccine-guardrail.php"
        zf.write(mu_file, arcname=f"php-vaccine-guardrail/php-vaccine-guardrail.php")

        # 2. Bundled Core Vaccine Serum
        vaccine_file = ROOT / "src" / "vaccine.php"
        zf.write(vaccine_file, arcname=f"php-vaccine-guardrail/src/vaccine.php")

        # 3. Bundled Legacy MySQL Shim
        shim_file = ROOT / "src" / "shims" / "mysql_shim.php"
        zf.write(shim_file, arcname=f"php-vaccine-guardrail/src/shims/mysql_shim.php")

        # 4. Readme and License
        zf.write(ROOT / "README.md", arcname="php-vaccine-guardrail/README.md")
        if (ROOT / "LICENSE").exists():
            zf.write(ROOT / "LICENSE", arcname="php-vaccine-guardrail/LICENSE")

    # Compute SHA-256
    hasher = hashlib.sha256()
    with open(zip_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    checksum = hasher.hexdigest()

    checksum_file = DIST_DIR / "SHA256SUMS"
    with open(checksum_file, "a") as f:
        f.write(f"{checksum}  {ZIP_NAME}\n")

    print(f"[+] Successfully built: {zip_path}")
    print(f"[+] SHA-256: {checksum}")
    return zip_path, checksum

if __name__ == "__main__":
    build_wordpress_zip()
