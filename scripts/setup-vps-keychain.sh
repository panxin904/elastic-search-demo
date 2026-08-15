#!/usr/bin/env bash
# Save VPS root password to macOS keychain (one-time setup).
# After this, you can retrieve it with:
#   security find-generic-password -s vps-root -w
#
# Usage:
#   ./setup-vps-keychain.sh <password>
# or interactive:
#   ./setup-vps-keychain.sh

set -e

if [[ "$OSTYPE" != "darwin"* ]]; then
  echo "This script only works on macOS (uses 'security' command)." >&2
  exit 1
fi

if [[ $# -ge 1 ]]; then
  PW="$1"
else
  read -r -s -p "Enter VPS root password: " PW
  echo
fi

if [[ -z "$PW" ]]; then
  echo "Password cannot be empty." >&2
  exit 1
fi

# -U updates an existing entry, creates one if absent
security add-generic-password -s vps-root -a root -w "$PW" -U

echo "✓ Saved to keychain (service=vps-root, account=root)."
echo
echo "Test retrieval:"
security find-generic-password -s vps-root -w
echo
echo "Use in deploy script:"
echo '  PW=$(security find-generic-password -s vps-root -w)'
echo '  printf "%s\n" "$PW" | bash release/deploy-fs.sh'
echo
echo "Use in smoke test:"
echo '  SITES_HUB_PASSWORD=$(security find-generic-password -s vps-root -w) python3 scripts/smoke.py'
