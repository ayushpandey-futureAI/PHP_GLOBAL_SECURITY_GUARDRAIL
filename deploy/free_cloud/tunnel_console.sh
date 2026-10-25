#!/usr/bin/env bash
# ==============================================================================
# ZERO-COST PUBLIC HTTPS CLOUDFLARE TUNNEL FOR FLEET CONSOLE
# ==============================================================================
# Exposes the Central Management Console to a public HTTPS URL for free
# without port-forwarding, static IPs, or firewall modifications.
#
# Usage:
#   bash deploy/free_cloud/tunnel_console.sh [--port 8080]
# ==============================================================================
set -euo pipefail

PORT=8080
if [[ "${1:-}" == "--port" && -n "${2:-}" ]]; then
    PORT="$2"
fi

GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}==================================================================${NC}"
echo -e "${CYAN}   ZERO-COST PUBLIC TUNNEL FOR PHP VACCINE FLEET CONSOLE          ${NC}"
echo -e "${CYAN}==================================================================${NC}"

if command -v cloudflared >/dev/null 2>&1; then
    echo -e "${GREEN}[+] Starting Cloudflare Quick Tunnel on port ${PORT}...${NC}"
    cloudflared tunnel --url "http://localhost:${PORT}"
else
    echo -e "${CYAN}[i] cloudflared not found. Falling back to zero-install SSH tunnel (localhost.run)...${NC}"
    echo -e "${GREEN}[+] Public HTTPS endpoint will appear below:${NC}"
    ssh -R 80:localhost:"${PORT}" nokey@localhost.run
fi
