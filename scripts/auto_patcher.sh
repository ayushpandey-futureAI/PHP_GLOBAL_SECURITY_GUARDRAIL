#!/usr/bin/env bash
# ==============================================================================
# PHP UNIVERSAL SECURITY VACCINE - CONTINUOUS ONLINE AUTO-PATCHER
# ==============================================================================
# Checks for upstream security updates, new threat signatures, and CVE patches
# directly from GitHub and atomically hot-patches the running server.
#
# Usage:
#   sudo bash scripts/auto_patcher.sh [--check] [--force]
# ==============================================================================
set -euo pipefail

REPO="ayushpandey-futureAI/PHP_GLOBAL_SECURITY_GUARDRAIL"
BRANCH="main"
GITHUB_RAW="https://raw.githubusercontent.com/${REPO}/${BRANCH}"
GITHUB_API="https://api.github.com/repos/${REPO}/commits/${BRANCH}"

VACCINE_DIR="/etc/php-vaccine"
VACCINE_TARGET="${VACCINE_DIR}/vaccine.php"
SHIM_TARGET="${VACCINE_DIR}/shims/mysql_shim.php"
SHA_FILE="${VACCINE_DIR}/.installed_sha"
PATCH_LOG="/var/log/php-vaccine-patcher.log"

GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${CYAN}[*] PHP Universal Security Vaccine - Online Auto-Patcher${NC}"

# Check root permissions
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}[ERROR] Auto-patcher requires root privileges.${NC}"
    exit 1
fi

CHECK_ONLY=0
FORCE=0
for arg in "$@"; do
    if [[ "${arg}" == "--check" ]]; then
        CHECK_ONLY=1
    elif [[ "${arg}" == "--force" ]]; then
        FORCE=1
    fi
done

# 1. Fetch Remote Commit SHA
echo -e "${CYAN}[1/3] Checking latest upstream release from GitHub...${NC}"
LATEST_SHA=$(curl -sSL -H "User-Agent: PHP-Vaccine-Patcher" "${GITHUB_API}" | grep '"sha":' | head -n 1 | cut -d '"' -f 4 || echo "")

if [ -z "${LATEST_SHA}" ]; then
    echo -e "${YELLOW}[!] Warning: Unable to query GitHub API. Falling back to direct raw download...${NC}"
    LATEST_SHA="latest-$(date +%s)"
fi

CURRENT_SHA=""
if [ -f "${SHA_FILE}" ]; then
    CURRENT_SHA=$(cat "${SHA_FILE}")
fi

echo "      -> Installed Version SHA: ${CURRENT_SHA:0:10:-None}"
echo "      -> Upstream Version SHA:  ${LATEST_SHA:0:10}"

if [ "${CURRENT_SHA}" == "${LATEST_SHA}" ] && [ "${FORCE}" -eq 0 ]; then
    echo -e "${GREEN}[+] System is already up to date with the latest security signatures.${NC}"
    exit 0
fi

if [ "${CHECK_ONLY}" -eq 1 ]; then
    echo -e "${YELLOW}[!] Update available. Run without --check to apply patch.${NC}"
    exit 0
fi

# 2. Download and Verify New Serum
echo -e "${CYAN}[2/3] Downloading latest vaccine serum and shims...${NC}"
TMP_VACCINE="/tmp/vaccine_new.php"
TMP_SHIM="/tmp/mysql_shim_new.php"

curl -sSL "${GITHUB_RAW}/src/vaccine.php" -o "${TMP_VACCINE}"
curl -sSL "${GITHUB_RAW}/src/shims/mysql_shim.php" -o "${TMP_SHIM}"

# Verify file integrity
if [ ! -s "${TMP_VACCINE}" ] || ! grep -q "PHP_VACCINE_LOADED" "${TMP_VACCINE}"; then
    echo -e "${RED}[ERROR] Downloaded vaccine serum failed validation check. Aborting patch.${NC}"
    rm -f "${TMP_VACCINE}" "${TMP_SHIM}"
    exit 1
fi

# 3. Atomic Hot-Swap
echo -e "${CYAN}[3/3] Atomically hot-patching runtime guardrail...${NC}"
mkdir -p "${VACCINE_DIR}/shims"
mv "${TMP_VACCINE}" "${VACCINE_TARGET}"
chmod 0644 "${VACCINE_TARGET}"

if [ -s "${TMP_SHIM}" ]; then
    mv "${TMP_SHIM}" "${SHIM_TARGET}"
    chmod 0644 "${SHIM_TARGET}"
fi

echo "${LATEST_SHA}" > "${SHA_FILE}"
chmod 0600 "${SHA_FILE}"

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
echo "[${TIMESTAMP}] [PATCH_APPLIED] Updated to upstream commit ${LATEST_SHA}" >> "${PATCH_LOG}"

echo -e "${GREEN}==================================================================${NC}"
echo -e "${GREEN} [SUCCESS] Patch applied atomically! No server restart required.  ${NC}"
echo -e "${GREEN} Latest SHA: ${LATEST_SHA:0:10} | Log: ${PATCH_LOG}${NC}"
echo -e "${GREEN}==================================================================${NC}"
