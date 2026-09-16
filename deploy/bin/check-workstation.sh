#!/usr/bin/env bash
# Workstation check for the software-factory loop (macOS). One line per requirement:
# OK / MISSING / SKIP, and exit 1 if a REQUIRED item is missing. Read-only: it changes
# nothing. Pair with deploy/01-workstation-macos.md, which says how to install each item.
#
# Usage: bash deploy/bin/check-workstation.sh [--pm] [--consort-root PATH]
#   --pm            the PM profile: skips the engineer-only items (sensors, reviewers, scanners)
#   --consort-root  Consort checkout or plugin root the caller will invoke (default: ~/git/consort)
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PM=0
CONSORT_ROOT=""
while [ $# -gt 0 ]; do
  case "$1" in
    --pm) PM=1; shift ;;
    --consort-root)
      if [ $# -lt 2 ]; then
        echo "check-workstation: --consort-root needs a path" >&2
        echo "usage: bash deploy/bin/check-workstation.sh [--pm] [--consort-root PATH]" >&2
        exit 1
      fi
      CONSORT_ROOT="$2"
      shift 2
      ;;
    *)
      echo "check-workstation: unknown argument: $1" >&2
      echo "usage: bash deploy/bin/check-workstation.sh [--pm] [--consort-root PATH]" >&2
      exit 1
      ;;
  esac
done
[ -n "$CONSORT_ROOT" ] || CONSORT_ROOT="$HOME/git/consort"
fail=0
# The runtime's config directory: a canvas or multiplexer runtime may set CLAUDE_CONFIG_DIR, and a
# plugin or marketplace registered under one directory is absent under the other. Run the checker
# under each environment you use; it reports which one it read.
CFG="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
ok()   { printf 'OK       %-28s %s\n' "$1" "${2:-}"; }
miss() { printf 'MISSING  %-28s %s\n' "$1" "${2:-}"; fail=1; }
warn() { printf 'OPTIONAL %-28s %s\n' "$1" "${2:-}"; }
skip() { printf 'SKIP     %-28s %s\n' "$1" "${2:-}"; }
have() { command -v "$1" >/dev/null 2>&1; }
ver()  { "$@" 2>/dev/null | head -1 | tr -d '\n'; }
req()  { if have "$1"; then ok "$1" "$(ver "${@:2}")"; else miss "$1" "$3"; fi; }
opt()  { if have "$1"; then ok "$1" "$(ver "${@:2}")"; else warn "$1" "not on PATH"; fi; }
plugin_enabled() { CFG="$CFG" python3 - "$1" <<'PY' 2>/dev/null
import json,os,sys
p=os.path.join(os.environ['CFG'],'settings.json')
d=json.load(open(p)) if os.path.exists(p) else {}
sys.exit(0 if d.get('enabledPlugins',{}).get(sys.argv[1]) else 1)
PY
}
marketplace_known() { CFG="$CFG" python3 - "$1" <<'PY' 2>/dev/null
import json,os,sys
p=os.path.join(os.environ['CFG'],'plugins/known_marketplaces.json')
d=json.load(open(p)) if os.path.exists(p) else {}
sys.exit(0 if sys.argv[1] in d else 1)
PY
}

echo "== agent runtime (config dir: $CFG)"
req claude claude --version
if have claude && claude auth status >/dev/null 2>&1; then ok "claude auth" "logged in"; else warn "claude auth" "run: claude  (log in once)"; fi
req git git --version
req gh gh --version
if have gh && gh auth status >/dev/null 2>&1; then ok "gh auth" "logged in"; else miss "gh auth" "run: gh auth login"; fi
req jq jq --version
req python3 python3 --version
req node node --version
if [ $PM -eq 1 ]; then skip uv "PM profile"; skip pnpm "PM profile"; else req uv uv --version; req pnpm pnpm --version; fi
req memspec memspec --version
req memspec-mcp true "npm install -g memspec (ships memspec-mcp)"
if grep -qs '^min-release-age=' "$HOME/.npmrc"; then warn "npm min-release-age set" "a memspec pin younger than that needs --min-release-age=0 on the install line (see guide section 2)"; fi
[ -d "$HOME/.memspec" ] && ok "~/.memspec store" "$(ls "$HOME/.memspec/memory" 2>/dev/null | wc -l | tr -d ' ') files" || miss "~/.memspec store" "run: memspec init ~/.memspec"
if have claude && claude mcp list 2>/dev/null | grep -q '^memspec'; then ok "memspec MCP (user scope)"; else miss "memspec MCP (user scope)" "claude mcp add --scope user memspec -e MEMSPEC_ROOT=\$HOME/.memspec -- memspec-mcp"; fi
for h in memspec-session-start.js memspec-consolidate.js; do [ -f "$CFG/hooks/$h" ] && ok "hook $h" || warn "hook $h" "memspec init installs it"; done

echo "== plugins (user scope)"
if [ $PM -eq 1 ]; then
  for p in pm-workspace@software-factory secret-guard@software-factory; do plugin_enabled "$p" && ok "plugin $p" || miss "plugin $p" "claude plugin install $p"; done
  plugin_enabled claude-hud@claude-hud && ok "plugin claude-hud@claude-hud" || warn "plugin claude-hud@claude-hud" "optional for a PM"
else
  for p in claude-hud@claude-hud secret-guard@software-factory; do plugin_enabled "$p" && ok "plugin $p" || miss "plugin $p" "claude plugin install $p"; done
fi
plugin_enabled consort@consort && ok "plugin consort@consort" || { [ $PM -eq 1 ] && skip "plugin consort@consort" "PM profile" || miss "plugin consort@consort" "claude plugin marketplace add siimvene/consort && claude plugin install consort@consort"; }
marketplace_known software-factory && ok "marketplace software-factory" || miss "marketplace software-factory" "claude plugin marketplace add <path>/software-factory/deploy/marketplace"
marketplace_known chisle && ok "marketplace chisle" || { [ $PM -eq 1 ] && skip "marketplace chisle" "PM profile" || warn "marketplace chisle" "registered per project by the scaffold (pinned tag)"; }

if [ $PM -eq 1 ]; then
  echo "== PM profile: engineer-only sections skipped (sensors, reviewers, scanners, containers)"
else
  echo "== second vendor (verify gate)"
  echo "reviewer contract: process environment (Claude settings are not the panel env)"
  python3 "$HERE/check-reviewers.py" --consort-root "$CONSORT_ROOT" || fail=1

  echo "== sensors"
  req enola enola --version "release binary from github.com/enola-labs/enola"
  req ripwire ripwire --version "github.com/redhat-et/ripwire installer"
  req lizard lizard --version "uv tool install lizard==1.23.0"
  opt ast-grep ast-grep --version
  [ -d "$HOME/git/cleat/quality/bin" ] && ok "cleat checkout" "$(git -C "$HOME/git/cleat" rev-parse --short HEAD 2>/dev/null)" || miss "cleat checkout" "git clone https://github.com/siimvene/cleat ~/git/cleat"

  echo "== scanners and containers"
  req trivy trivy --version
  req docker docker --version "OrbStack or Docker Desktop"
  if have docker && docker info >/dev/null 2>&1; then ok "docker daemon" "up"; else miss "docker daemon" "start OrbStack / Docker Desktop"; fi
  opt sonar-scanner sonar-scanner --version
  if have docker && docker ps --format '{{.Names}}' 2>/dev/null | grep -qx sonarqube; then ok "sonarqube container" "up"; else warn "sonarqube container" "optional static-analysis leg; see 01-workstation-macos.md"; fi
  [ -r "$HOME/.config/sonar/env" ] && ok "~/.config/sonar/env" || warn "~/.config/sonar/env" "SONAR_TOKEN + SONAR_HOST_URL, sourced from ~/.zshenv"
  opt playwright-cli playwright-cli --version
  opt tmux tmux -V
fi

echo "== ledger"
[ -r "$HOME/.config/factory/jira.env" ] && ok "~/.config/factory/jira.env" || warn "~/.config/factory/jira.env" "JIRA_BASE_URL, JIRA_USER_EMAIL, JIRA_PROJECT_KEY, FACTORY_REPO"
if security find-generic-password -s factory-jira-api-token >/dev/null 2>&1; then ok "keychain factory-jira-api-token"; else warn "keychain factory-jira-api-token" "security add-generic-password -s factory-jira-api-token -a <email> -w"; fi
[ -x "$HOME/.local/bin/jira" ] && ok "~/.local/bin/jira" || warn "~/.local/bin/jira" "copy deploy/templates/bin/jira"

echo
if [ $fail -eq 0 ]; then echo "workstation: every REQUIRED item present"; else echo "workstation: REQUIRED items missing (see MISSING lines)"; fi
exit $fail
