#!/usr/bin/env bash
# ==============================================================================
# PHP UNIVERSAL SECURITY VACCINE - FLEET CONSOLE SERVER LAUNCHER
# ==============================================================================
# Launches the Central Management Web Console & REST API online.
# Supports PHP standalone web server or production Docker stack.
#
# Usage:
#   bash scripts/serve_console.sh [--port 8080] [--docker]
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="${SCRIPT_DIR}/.."
CONSOLE_DIR="${ROOT_DIR}/src/console"

PORT=8080
USE_DOCKER=0

while [[ $# -gt 0 ]]; do
    case "$1" in
        --port)
            PORT="$2"
            shift 2
            ;;
        --docker)
            USE_DOCKER=1
            shift
            ;;
        *)
            shift
            ;;
    esac
done

GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}==================================================================${NC}"
echo -e "${CYAN}  STARTING PHP UNIVERSAL VACCINE FLEET CONSOLE ONLINE             ${NC}"
echo -e "${CYAN}==================================================================${NC}"

if [ "${USE_DOCKER}" -eq 1 ]; then
    echo -e "${GREEN}[+] Launching Production Docker Compose Stack...${NC}"
    cd "${ROOT_DIR}/docker"
    docker compose up -d --build
    echo -e "${GREEN}[+] Console active online via NGINX: http://localhost:${PORT}/${NC}"
else
    if command -v php >/dev/null 2>&1; then
        echo -e "${GREEN}[+] Launching PHP Built-in Web Server on port ${PORT}...${NC}"
        echo -e "${GREEN}[+] Live URL: http://0.0.0.0:${PORT}/${NC}"
        echo -e "${CYAN}[i] Press Ctrl+C to stop.${NC}"
        php -S "0.0.0.0:${PORT}" -t "${CONSOLE_DIR}"
    else
        echo -e "${CYAN}[i] PHP CLI not found locally. Launching via Docker Compose...${NC}"
        cd "${ROOT_DIR}/docker"
        docker compose up -d
        echo -e "${GREEN}[+] Console active online via Docker: http://localhost:${PORT}/${NC}"
    fi
fi
