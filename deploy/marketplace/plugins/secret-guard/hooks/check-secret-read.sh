#!/usr/bin/env bash
# secret-guard: block agent reads of secret-bearing files.
# Claude Code PreToolUse hook — stdin carries the tool call JSON; exit 2 blocks
# the call and feeds stderr back to the model as the reason.
set -uo pipefail

payload="$(cat)"

command -v jq >/dev/null 2>&1 || exit 0   # no jq: fail open, guard is best-effort

tool="$(printf '%s' "$payload" | jq -r '.tool_name // empty')"
target=""
case "$tool" in
  Read)  target="$(printf '%s' "$payload" | jq -r '.tool_input.file_path // empty')" ;;
  Bash)  target="$(printf '%s' "$payload" | jq -r '.tool_input.command // empty')" ;;
  *)     exit 0 ;;
esac
[ -z "$target" ] && exit 0

lc="$(printf '%s' "$target" | tr '[:upper:]' '[:lower:]')"

# Allowlist: templates and examples are not secrets.
case "$lc" in
  *.env.example*|*.env.tpl*|*.env.template*|*.env.sample*) exit 0 ;;
esac

# Blocklist: env files, private keys, cloud/agent credentials, kubeconfigs.
BLOCK='(^|[/ "'\''=])\.env($|[. "'\''])|\.envrc|id_rsa|id_ed25519|id_ecdsa|\.pem($|[ "'\''])|\.p12|\.pfx|\.keystore|kubeconfig|\.kube/config|\.aws/credentials|\.npmrc|\.pypirc|auth\.json|credentials\.json|\.netrc|secrings|\.gnupg/'
if printf '%s' "$lc" | grep -qE "$BLOCK"; then
  echo "secret-guard: blocked — '$target' matches a secret-file pattern. Secrets are fetched at runtime (op run / ADC), never read into context. If this is a false positive (e.g. a template), rename it *.example/*.tpl or ask the user to read it themselves." >&2
  exit 2
fi
exit 0
