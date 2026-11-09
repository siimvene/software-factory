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
# Exit codes of `enola check`: 0 clean, 1 the policy was violated, 2 usage or a
# blocking error (no baseline, run from the wrong directory), 3 incomparable
# baseline. All non-zero exits block once: a gate that did not run is not a pass.
set -u
export PATH="$HOME/.local/bin:$PATH"
command -v enola >/dev/null 2>&1 || exit 0
# The checkout the session is working in, worktrees included (CLAUDE_PROJECT_DIR keeps
# pointing at the checkout the session started in after it enters a worktree).
cd "$(git rev-parse --show-toplevel 2>/dev/null || echo "${CLAUDE_PROJECT_DIR:-$PWD}")" || exit 0
input=$(cat 2>/dev/null || :)
# No baseline here: a worktree entered mid-session never ran SessionStart, and .enola/ is
# gitignored. Checking would only report "no baseline", and grading another checkout would
# grade the wrong code; say so once and leave this change to CI's enola job, which pins at base.
if [ ! -d .enola ]; then
  echo "enola: no baseline in $(pwd) (worktree entered mid-session?); the architecture delta is left to CI's enola job. Pin one at the base commit to check locally." >&2
  exit 0
fi
enola hook stop <<<"$input" >/dev/null 2>&1 || :
out=$(enola check --fail-on=layers,cycles,intent 2>&1)
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
