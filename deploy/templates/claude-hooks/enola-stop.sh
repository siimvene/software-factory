#!/usr/bin/env bash
# Claude Code Stop hook: the enola architecture gate, able to fail.
#
# `enola hook stop` carries no policy and exits 0 on a planted layering violation
# (wheel-green run, PR #22). This runs it anyway (whatever session bookkeeping it
# pairs with `enola hook session-start`), then `enola check --fail-on=...` from the
# project root, and turns a non-zero exit into the Stop hook's exit 2 with the
# output on stderr — once. On the retry (`stop_hook_active` true on stdin) the
# same result is reported and the stop is released, the way cleat's hook does it,
# so a violation the agent cannot fix does not trap it. enola missing: exit 0.
#
# Worktrees. The project root is the hook input's `cwd` (the session's real location),
# then the git top level of the process directory, never CLAUDE_PROJECT_DIR alone: after a
# mid-session worktree switch that variable still names the starting checkout, and a hook
# rooted on it graded that checkout and was blind to the change (measured on the reference
# implementation). A worktree has no pinned baseline of its own (.enola/ is gitignored); when
# the main checkout of the repository has one, the check grades against that, so the gate
# runs in every worktree the way it runs in the main checkout. No baseline anywhere is still
# a blocking exit 2. The fallback is only as current as the main checkout's baseline: one
# pinned under an older enola or another producer set grades a partial verdict (enola says
# so in its output), so re-pin it there after pulling (`enola baseline pin .`).
#
# Exit codes of `enola check`: 0 clean, 1 the policy was violated, 2 usage or a
# blocking error (no baseline, run from the wrong directory), 3 incomparable
# baseline. All non-zero exits block once: a gate that did not run is not a pass.
set -u
export PATH="$HOME/.local/bin:$PATH"
command -v enola >/dev/null 2>&1 || exit 0
input=$(cat 2>/dev/null || :)
root=$(printf '%s' "$input" | python3 -I -c 'import json, sys
try:
    cwd = json.load(sys.stdin).get("cwd")
except Exception:
    cwd = None
print(cwd if isinstance(cwd, str) else "")' 2>/dev/null || :)
[ -n "$root" ] && [ -d "$root" ] || root=$PWD
cd "$root" || exit 0
# A cwd below the root (a subdirectory session) still grades the whole tree.
cd "$(git rev-parse --show-toplevel 2>/dev/null || echo "${CLAUDE_PROJECT_DIR:-$PWD}")" || exit 0
baseline_args=()
if [ ! -f .enola/baseline/facts.jsonl ]; then
  # The main working tree: the common git dir's core.worktree when set (a submodule's git
  # dir lives under the superproject's .git/modules), else the first entry git lists
  # (a plain repository, or one made with --separate-git-dir).
  common=$(git rev-parse --path-format=absolute --git-common-dir 2>/dev/null)
  wt=$(git --git-dir="${common:-/nonexistent}" config core.worktree 2>/dev/null)
  if [ -n "$wt" ]; then
    main_root=$(cd "$common" 2>/dev/null && cd "$wt" 2>/dev/null && pwd -P)
  else
    main_root=$(git worktree list --porcelain 2>/dev/null | sed -n '1s/^worktree //p')
  fi
  main_root=${main_root:-/nonexistent}
  [ -f "$main_root/.enola/baseline/facts.jsonl" ] && baseline_args=(--baseline="$main_root/.enola/baseline")
fi
enola hook stop <<<"$input" >/dev/null 2>&1 || :
out=$(enola check --fail-on=layers,cycles,intent "${baseline_args[@]+"${baseline_args[@]}"}" 2>&1)
code=$?
[ "$code" -eq 0 ] && exit 0
if [ "$code" -eq 1 ]; then
  echo "enola: the architecture policy was violated (layers, cycles, intent):" >&2
else
  echo "enola: the architecture gate did not run (enola check exit $code); this is not a pass:" >&2
fi
echo "$out" >&2
if printf '%s' "$input" | grep -Eq '"stop_hook_active": *true'; then
  echo "enola: reported once already; releasing the stop." >&2
  exit 0
fi
exit 2
