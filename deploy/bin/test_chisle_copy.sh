#!/usr/bin/env bash
# test_chisle_copy.sh — the two changes the software-factory copy of chisle makes to
# upstream (deploy/marketplace/plugins/chisle/VENDORED.md): its SessionStart hook neither
# tells the model to edit the user's settings nor calls the network by default.
#
#   bash deploy/bin/test_chisle_copy.sh
#
# Runs the real hook against throwaway config directories, with a recorder in place of
# fetch, so no run touches the network. Needs node. HOOK=<path> points it at another copy
# of chisle-activate.js (its sibling modules and ../.claude-plugin/plugin.json are read
# from beside it).
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
HOOK="${HOOK:-$HERE/../marketplace/plugins/chisle/hooks/chisle-activate.js}"
case "$HOOK" in /*) : ;; *) HOOK="$PWD/$HOOK" ;; esac
[ -f "$HOOK" ] || { echo "test_chisle_copy.sh: no hook at $HOOK" >&2; exit 2; }
command -v node >/dev/null 2>&1 || { echo "test_chisle_copy.sh: node is required" >&2; exit 2; }
W="$(mktemp -d)" && [ -n "$W" ] && [ -d "$W" ] || { echo "test_chisle_copy.sh: mktemp -d failed" >&2; exit 2; }
trap 'rm -rf "$W"' EXIT
fail=0
expect() { local label="$1"; shift; if "$@" >/dev/null 2>&1; then echo "  ok   $label"; else echo "  FAIL $label"; fail=1; fi; }
# Node's built-in fetch ignores HTTP(S)_PROXY, so a refusing proxy isolates nothing. The
# hook is run with this preload instead: it replaces fetch with a recorder that appends
# each requested URL to $FETCH_LOG and answers like the registry would. A run that calls
# out leaves a line there whether or not the machine is online.
cat > "$W/fetch-recorder.js" <<'JS'
const fs = require('fs');
globalThis.fetch = async (url) => {
  fs.appendFileSync(process.env.FETCH_LOG, String(url) + '\n');
  return { ok: true, status: 200, json: async () => ({ version: '99.0.0' }), text: async () => '{"version":"99.0.0"}' };
};
JS
# run <name> [VAR=value ...]: the hook with a fresh, empty config dir (no settings.json)
# and a startup payload on stdin.
run() {
  local name="$1"; shift
  mkdir -p "$W/$name"
  printf '{"source":"startup"}' | env -i PATH="$PATH" HOME="$W/$name" CLAUDE_CONFIG_DIR="$W/$name" \
    FETCH_LOG="$W/$name.fetch" "$@" node --require "$W/fetch-recorder.js" "$HOOK" > "$W/$name.out" 2>"$W/$name.err"
}
called() { [ -s "$W/$1.fetch" ]; }
has()   { grep -q -- "$2" "$W/$1.out"; }
lacks() { ! grep -q -- "$2" "$W/$1.out"; }

echo "by default the hook teaches the ruleset and asks for nothing"
run default
expect "the ruleset is emitted"                        test -s "$W/default.out"
expect "no status-line setup text"                     lacks default 'STATUSLINE SETUP NEEDED'
expect "no instruction to offer a settings edit"       lacks default 'Proactively offer'
expect "no settings.json path is handed to the model"  lacks default 'settings.json'
expect "no network call is made"                       bash -c "! [ -s '$W/default.fetch' ]"
expect "no update-check cache is written"              test ! -e "$W/default/.chisle-update-check.json"

echo "the nudge is still there for whoever opts in (so the default check above can fail)"
run optin CHISLE_STATUSLINE_NUDGE=1
expect "opt-in emits the status-line setup text"       has optin 'STATUSLINE SETUP NEEDED'

echo "the update check is still there for whoever opts in (so the no-call check above can fail)"
run update CHISLE_UPDATE_CHECK=1
expect "opt-in calls the registry"                     called update
expect "and it is the npm registry it asks"            grep -q 'registry.npmjs.org' "$W/update.fetch"
expect "and the model is told about the newer major"   has update 'CHISLE UPDATE AVAILABLE'

echo "a configured status line keeps even the opt-in quiet"
mkdir -p "$W/configured" && printf '{"statusLine":{"type":"command","command":"true"}}' > "$W/configured/settings.json"
run configured CHISLE_STATUSLINE_NUDGE=1
expect "no nudge when a status line exists"            lacks configured 'STATUSLINE SETUP NEEDED'

if [ "$fail" = 0 ]; then echo "test_chisle_copy.sh: all passed."; else echo "test_chisle_copy.sh: FAILED."; fi
exit "$fail"
