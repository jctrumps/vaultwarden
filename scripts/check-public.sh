#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
echo 'Scanning working files for likely secrets/private material (heuristic; not a guarantee)...'
if command -v git >/dev/null && git rev-parse --git-dir >/dev/null 2>&1; then
  if git ls-files | grep -E '(^|/)(settings\.env|\.env|terraform\.tfvars|hosts\.yml|id_ed25519|.*\.tfstate)$'; then echo 'FAIL: potentially sensitive tracked file'; exit 1; fi
fi
if grep -RInE --exclude-dir=.git --exclude='check-public.sh' '(BEGIN (OPENSSH|RSA|EC) PRIVATE KEY|CF_TUNNEL_TOKEN=|CLOUDFLARE_API_TOKEN=|BW_INSTALLATION_KEY=[a-z0-9_-]{30,}|proxmox_api_token[[:space:]]*=[[:space:]]*"[^" ]{18,}")' .; then
  echo 'FAIL: potential embedded secret'; exit 1
fi
printf 'No obvious embedded secrets detected; human review still mandatory.\n'
