#!/usr/bin/env bash
# Run a Claude Code hook command at the root of the repository the session is working in.
#
#   bash scripts/claude-hooks/at-root.sh sh -c '<command>'
#
# A hook's process directory is not a reliable "where the session is": a session that entered
# a worktree, or a call sent from a cloud session, can start the hook elsewhere, and
# CLAUDE_PROJECT_DIR stays on the checkout the session started in. The authoritative answer is
# the `cwd` field of the hook's stdin JSON, so this reads it first, falls back to the process
# directory, takes that directory's git top level (else CLAUDE_PROJECT_DIR's), changes there, and
# runs the command with the same stdin, since the hooks it wraps read their payload from it.
set -u
input=$(cat 2>/dev/null || :)
dir=$(printf '%s' "$input" | python3 -I -c '
import json, sys
try:
    cwd = json.load(sys.stdin).get("cwd")
except Exception:
    cwd = None
print(cwd if isinstance(cwd, str) else "")' 2>/dev/null || :)
[ -n "$dir" ] && [ -d "$dir" ] || dir=$PWD
root=$(git -C "$dir" rev-parse --show-toplevel 2>/dev/null) \
  || root=$(git -C "${CLAUDE_PROJECT_DIR:-$dir}" rev-parse --show-toplevel 2>/dev/null) \
  || root=${CLAUDE_PROJECT_DIR:-$dir}
cd "$root" || exit 0
printf '%s' "$input" | "$@"
