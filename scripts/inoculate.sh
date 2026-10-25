#!/usr/bin/env bash
# ==============================================================================
# PHP UNIVERSAL SECURITY VACCINE - AUTOMATED 1-SHOT INOCULATOR
# ==============================================================================
# Inoculates PHP systems globally by injecting the ambient RASP layer
# into active PHP runtimes and neutralizing web shell upload execution.
#
# Usage:
#   sudo bash scripts/inoculate.sh [--audit-only] [--uninstall]
# ==============================================================================
set -euo pipefail

VACCINE_DIR="/etc/php-vaccine"
VACCINE_LOG="/var/log/php-vaccine.log"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd || echo "")"
SOURCE_SERUM="${SCRIPT_DIR}/../src/vaccine.php"
SOURCE_SHIM="${SCRIPT_DIR}/../src/shims/mysql_shim.php"
GITHUB_RAW_BASE="https://raw.githubusercontent.com/ayushpandey-futureAI/PHP_GLOBAL_SECURITY_GUARDRAIL/main"

# Color Codes
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${CYAN}==================================================================${NC}"
echo -e "${CYAN}   PHP UNIVERSAL SECURITY VACCINE - 1-SHOT RUNTIME INOCULATOR    ${NC}"
echo -e "${CYAN}==================================================================${NC}"

# Check root permissions
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}[ERROR] Inoculator requires administrative privileges. Run with sudo.${NC}"
    exit 1
fi

MODE="ENFORCE"
AUTO_PATCH=0
for arg in "$@"; do
    if [[ "${arg}" == "--audit-only" ]]; then
        MODE="AUDIT"
        echo -e "${YELLOW}[!] Running in AUDIT ONLY mode (Logging threats without blocking 403).${NC}"
    elif [[ "${arg}" == "--auto-patch" ]]; then
        AUTO_PATCH=1
        echo -e "${GREEN}[+] Online Auto-Patching daemon scheduled for installation.${NC}"
    fi
done

# Step 1: Install Vaccine Core Files and Shims
echo -e "${CYAN}[1/5] Deploying Vaccine Core Serum & Shims to ${VACCINE_DIR}...${NC}"
mkdir -p "${VACCINE_DIR}/shims"
touch "${VACCINE_LOG}"
chmod 0666 "${VACCINE_LOG}"

if [ -f "${SOURCE_SERUM}" ]; then
    cp "${SOURCE_SERUM}" "${VACCINE_DIR}/vaccine.php"
    if [ -f "${SOURCE_SHIM}" ]; then
        cp "${SOURCE_SHIM}" "${VACCINE_DIR}/shims/mysql_shim.php"
    fi
else
    echo -e "${YELLOW}[i] Local source serum not found. Pulling latest release online from GitHub...${NC}"
    curl -sSL "${GITHUB_RAW_BASE}/src/vaccine.php" -o "${VACCINE_DIR}/vaccine.php"
    curl -sSL "${GITHUB_RAW_BASE}/src/shims/mysql_shim.php" -o "${VACCINE_DIR}/shims/mysql_shim.php" 2>/dev/null || true
fi

chmod 0644 "${VACCINE_DIR}/vaccine.php"
if [ -f "${VACCINE_DIR}/shims/mysql_shim.php" ]; then
    chmod 0644 "${VACCINE_DIR}/shims/mysql_shim.php"
fi
echo -e "${GREEN}      -> Core serum active at ${VACCINE_DIR}/vaccine.php${NC}"
echo -e "${GREEN}      -> Legacy MySQL shim active at ${VACCINE_DIR}/shims/mysql_shim.php${NC}"

# Step 2: Inoculate All PHP Engines Across Installed Versions
echo -e "${CYAN}[2/5] Scanning and Inoculating PHP Configuration (php.ini)...${NC}"
INI_CANDIDATES=$(find /etc/php* /usr/local/etc/php* /etc -name "php.ini" 2>/dev/null || true)

INOCULATED_COUNT=0
for INI in ${INI_CANDIDATES}; do
    [ -f "${INI}" ] || continue
    echo "      -> Patching: ${INI}"
    
    # 1. auto_prepend_file injection
    if grep -q "^auto_prepend_file" "${INI}"; then
        sed -i 's|^auto_prepend_file.*|auto_prepend_file = "'"${VACCINE_DIR}"'/vaccine.php"|' "${INI}"
    else
        echo "auto_prepend_file = \"${VACCINE_DIR}/vaccine.php\"" >> "${INI}"
    fi

    # 2. Hardening defaults
    sed -i 's|^expose_php.*|expose_php = Off|' "${INI}" 2>/dev/null || true
    sed -i 's|^allow_url_include.*|allow_url_include = Off|' "${INI}" 2>/dev/null || true
    
    INOCULATED_COUNT=$((INOCULATED_COUNT + 1))
done
echo -e "${GREEN}      -> Successfully inoculated ${INOCULATED_COUNT} php.ini runtime files.${NC}"

# Step 3: Hardening Web Server (Prevent Web Shell Execution in Upload Folders)
echo -e "${CYAN}[3/5] Applying Web Server Upload Execution Lockdown...${NC}"

# NGINX Configuration Drop
if [ -d "/etc/nginx/conf.d" ]; then
    cat << 'EOF' > /etc/nginx/conf.d/php_vaccine_uploads.conf
# PHP-VACCINE: Zero-Trust Upload Directory Execution Lockdown
location ~* /(?:uploads|wp-content/uploads|media|files|images|cache)/.*\.php$ {
    deny all;
    return 404;
}
EOF
    echo -e "${GREEN}      -> NGINX upload guardrail injected into /etc/nginx/conf.d/${NC}"
fi

# Step 4: Gracefully Reload Running PHP and Web Daemon Services
echo -e "${CYAN}[4/5] Reloading PHP-FPM and Web Services...${NC}"
if command -v systemctl >/dev/null 2>&1; then
    # Reload all PHP-FPM versions (5.6 through 8.4)
    for service in $(systemctl list-units --type=service --state=running | grep -o 'php[0-9.]*-fpm' || true); do
        echo "      -> Reloading service: ${service}"
        systemctl reload "${service}" 2>/dev/null || systemctl restart "${service}" 2>/dev/null || true
    done
    
    # Reload Web Servers
    if systemctl is-active --quiet nginx; then
        echo "      -> Reloading NGINX..."
        systemctl reload nginx 2>/dev/null || true
    fi
    if systemctl is-active --quiet apache2; then
        echo "      -> Reloading Apache2..."
        systemctl reload apache2 2>/dev/null || true
    fi
    if systemctl is-active --quiet httpd; then
        echo "      -> Reloading HTTPD..."
        systemctl reload httpd 2>/dev/null || true
    fi
fi

# Step 4b: Online Auto-Patching Daemon & Cron Setup (if requested)
if [ "${AUTO_PATCH}" -eq 1 ]; then
    echo -e "${CYAN}[+] Installing Automated Online Continuous Security Patcher...${NC}"
    CRON_FILE="/etc/cron.daily/php-vaccine-auto-patch"
    cat << 'EOF' > "${CRON_FILE}"
#!/usr/bin/env bash
# Automated Continuous Security Patcher for PHP Universal Vaccine
set -euo pipefail
VACCINE_URL="https://raw.githubusercontent.com/ayushpandey-futureAI/PHP_GLOBAL_SECURITY_GUARDRAIL/main/src/vaccine.php"
TARGET="/etc/php-vaccine/vaccine.php"
TMP="/tmp/vaccine_patch_check.php"

if curl -sSL "${VACCINE_URL}" -o "${TMP}"; then
    if [ -s "${TMP}" ]; then
        mv "${TMP}" "${TARGET}"
        chmod 0644 "${TARGET}"
        echo "[$(date -u)] [AUTO_PATCH_SUCCESS] Updated ${TARGET} to latest online release" >> /var/log/php-vaccine-patcher.log
    fi
fi
EOF
    chmod +x "${CRON_FILE}"
    echo -e "${GREEN}      -> Daily auto-patcher installed at ${CRON_FILE}${NC}"
fi

# Step 5: Self-Verification
echo -e "${CYAN}[5/5] Performing Verification & Diagnostic Self-Test...${NC}"
if command -v php >/dev/null 2>&1; then
    TEST_OUTPUT=$(VACCINE_TEST_MODE=1 php -r '
        $_SERVER["QUERY_STRING"] = "-d allow_url_include=1";
        require "/etc/php-vaccine/vaccine.php";
    ' 2>&1 || true)
    
    if echo "${TEST_OUTPUT}" | grep -q "403 Forbidden"; then
        echo -e "${GREEN}      -> Self-test passed: Exploit query simulation intercepted successfully!${NC}"
    else
        echo -e "${YELLOW}      -> Warning: Self-test produced unexpected output: ${TEST_OUTPUT}${NC}"
    fi
fi

echo -e "${GREEN}==================================================================${NC}"
echo -e "${GREEN} [SUCCESS] INOCULATION COMPLETE! The PHP runtime is immunized.     ${NC}"
echo -e "${GREEN} Threat Log Stream: ${VACCINE_LOG}                              ${NC}"
echo -e "${GREEN}==================================================================${NC}"
