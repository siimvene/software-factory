# Two green PRs, main red twice (kvart, 2026-09-29)

An attended session was asked to merge five open PRs in the right order. Two of the merges
turned main red within 20 minutes, each by a PR whose own CI was green. The causes differ, so
they are recorded separately. All times UTC, all `[measured 2026-09-29]`.

## Setting

- Ruleset: 8 required checks, `strict_required_status_checks_policy: false` (a PR need not be
  up to date with main to merge). The forge account has no merge queue.
- PR CI runs an impact-selected backend slice (78 targets on the PR in case B). The full suite
  runs only on main (`backend-full`); a red there makes `revert-on-red` open a revert PR, it
  does not push to main.

## Case A: stale base (semantic conflict)

| Time | Event |
|---|---|
| before 13:16 | #340 (KVART-453) merges: the vote verdict moves from a label-matching `_compute_decision` to role-based `decision_line`, and `_decision_frame` adds one query per protocol build |
| 13:16:19 | #339 (KVART-67, 24 new test files, tests only) merges. Its CI was green on a base without #340; `mergeStateStatus` was `CLEAN` |
| next | on main: 1 test module fails to import (`_compute_decision`), 7 tests fail with `StopIteration` (the mocked session is one `execute` short) |

What would have caught it:

- `pytest --collect-only` on the whole suite catches the import error. It does not catch the 7
  `StopIteration` failures.
- Only a run on the combined tree catches all 8. A strict ruleset forces that run; a
  non-strict one never does.

Fix-forward #342, tests only (remove the class that tested the deleted function, whose
boundaries the new module's own tests cover; add the fourth `execute` to the mock). 41 passed,
two-vendor panel 0 findings, merged 13:38:12.

## Case B: impact selection omitted a repo-wide fence

| Time | Event |
|---|---|
| 2026-09-25 | the error-code fence (`test_error_code_translations`) lands: every code the backend emits must have a translation in all 4 locales |
| 09:13 | #335 (KVART-442/443) CI runs 78 impact-selected targets; the fence is not among them. The diff adds 2 error codes in the reading route with no translations |
| 13:16:08 | #335 merges; main's full-suite run on the merge commit fails |
| 13:43 | a third PR (#331) goes red on both A's import error and B's missing translations, neither of them its own |

This is not a stale base: the fence predates the PR. The selector maps a changed source file
to the tests that import it; a fence that scans the whole tree imports nothing specific, so it
is never selected. Fix-forward #344 (8 locale lines), merged 13:54:30.

## Case C: stale local ref, not a stale PR

- The shared checkout's local `main` was 114 commits behind `origin/main`.
- The repo's agent instructions said `git worktree add <scratch>/<slug> main`, so every new
  worktree started 114 commits stale.
- PR #333 carried migration `228_*`; main already had its own 228. Renumbered to 232 at merge
  time. Whether #333's 228 came from a stale base was not established. The mechanism fits: the
  migration rule is "check the latest number", and a stale tree answers with an old one.

## Re-check before merge, applied to the remaining PRs

With main moving under every open PR, the last three were each tested on a local merge with
current main before their merge:

- #341: its 24 test files plus the vote, meeting-quorum, registry-import and claim suites,
  501 passed; type check clean.
- #333 + #331 + main combined: 583 passed across both PRs' tests, the guards and the
  neighbouring bank rail; money path map resolves (9 entries); one migration head.

This is a hand step. It depends on the merger remembering it, which case A shows is not a
control.
