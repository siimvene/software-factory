# kvart dogfood, cycle 1 (2026-09-07)

> Source: the cycle-1 report written into the PM workspace's outputs folder at the end of the run, 2026-09-07.
> Copied near-verbatim, anonymised.

# The group SDLC dogfood on kvart — cycle 1 report (2026-09-07)

Ticket: the ticket file in the PM workspace, `associations-and-onboarding / 01 - Mandate signing link - admit anonymous visitors`
Code PR: siimvene/kvart#17 (`966f7d7c`, branch `fix/mandate-sign-public-route`)
Sister spec PR: siimvene/kvart-team-context#4 (branch `specs/mandate-sign-route-fix`)
Both open, owner merges by hand (ADR 0001 shortcut: no branch protection on the free plan).

## Wall-clock per stage

| Stage | Start | End | Elapsed | Notes |
|---|---|---|---|---|
| PM: pick ticket from findings, verify 3 candidates against code + prod | 02:40 | 02:44 | ~4 min | included a prod check on the auto-pay flag (1 HOA on, 0 payments initiated) |
| PM: draft ticket (`/jira` by hand), self-score readiness | 02:44 | 02:51 | ~7 min | 94/100 self-scored |
| Dev: worktree, deps (`pnpm install` 6 s, `uv sync` 1 s) | 02:51:26 | 02:52:30 | ~1 min | shared caches did their job |
| Dev: tests written first, unit case red on unfixed middleware | 02:52:30 | 02:53:01 | 30 s | exact bounce `/login?redirect=%2Fmandate-sign%2F…` |
| Dev: one-line fix, unit file green (101/101), lint | 02:53:01 | 02:53:26 | 25 s | |
| Dev: Playwright spec, stack boot, pass (17.8 s run) | 02:53:26 | 02:56:10 | ~3 min | first attempt lost to a missing `timeout` binary on macOS |
| Dev: negative e2e run (fix reverted, spec must fail) | 02:56:10 | 02:57:20 | ~1 min | `git stash` refused the intent-to-add file; file copy instead |
| Gate: scanner tier (`consort-scan.sh`, Trivy + Sonar) | 02:55 | 02:55 | <1 min | 515 pre-existing dep CVEs, none from this diff; Sonar truncated at 500 of 1495 |
| Gate: Codex cross-vendor review (`consort-review.sh`) | 02:55:57 | 03:03:03 | 7 min 06 s | 0 findings; probe `CODEX_ALIVE` first |
| Gate: blind security side-agent (Opus, non-inheriting) | 02:55 | 02:58 | 2 min 53 s | 0 findings, 2 info; 113k tokens, 19 tool calls |
| QA (`/qa` skill, headless Chromium fallback) | 02:58 | 03:02 | ~4 min | 10 surfaces, 0 CRITICAL/SERIOUS, 1 pre-existing MINOR |
| Commit + push + PR #17 | 02:58 | 03:03:37 | | PR opened the moment Codex returned |
| Sister spec PR #4 (hand-edited) | 03:03:37 | 03:05:10 | 1 min 33 s | |
| **Dev hat on → code PR open** | 02:51:26 | 03:03:37 | **12 min 11 s** | Codex review is 58% of it |
| **Dev hat on → sister PR open** | 02:51:26 | 03:05:10 | **13 min 44 s** | |
| Owner merge (both PRs, on request) + worktree cleanup | 03:08 | 03:12 | ~4 min | |
| Pre-deploy gate (smoke + changed-surface spec, local e2e) | 03:16:47 | 03:17:03 | 16 s | 2/2 green |
| Deploy (prod pull, frontend build, restart; no migration, no backend restart) | 03:17:27 | 03:18:06 | 39 s | prod was on `12c712c4` from 09-05; range had no backend or dependency changes |
| Prod probe (headless, anonymous, bogus token) | 03:19 | 03:19 | <1 min | stays on route, invalid-link state, no errors |
| **Dev hat on → live in prod** | 02:51:26 | 03:19 | **~28 min** | includes the human merge step |

Tokens: only the security side-agent reports its own count (113,435). The principal session's per-stage token use is not instrumented; a Stop-hook counter is the mechanical upgrade if this number matters for the group rollout.

## Outcome

- Fix: `/mandate-sign/*` added to the web public-route list. Root cause: the signing page and the fraud-report page shipped 2026-08-27 in two commits; only the second got the allowlist arm.
- Fences: middleware unit case (fails on main) and `frontend/e2e/mandate-sign-link.spec.ts` (fails on main, verified with a reverted middleware).
- Bonus finding from the security side-pass, verified: the old login bounce put the signing capability token into the `/login?redirect=` URL, so browser history and `/login` access logs captured it; the log scrubber only masks path-shaped tokens. The fix removes that leak.
- Memspec reconciliation on commit surfaced 7 entries touching the middleware; all still true (they describe other arms of the same guard), none corrected.

## Skipped or shortcut steps (each one is a finding about the process, not the product)

1. PM hat and dev hat ran in the same session (the plan said separate sessions). Cost: the dev pass inherited the PM's framing. Mitigated by the non-inheriting reviewers.
2. `/jira` skill in this copy of the PM template references `references/style-rules.md`, which does not exist. Drafted from `templates/Jira Story.md` only.
3. `kvart-team-context/specs/` stood in for `Features/` as the pipeline source (no `Features/` folder in this workspace).
4. Readiness was self-scored against the rubric; the skill's ticket write-back and improver loop did not run (no ticket system).
5. `update-specs-for-commits` is not installed here; the sister spec delta was hand-edited (agents-core §2 forbids hand edits; recorded as a cycle-1 shortcut in the PR body).
6. `check-specs.py` from the Day 1 bootstrap lived in a scratchpad that is gone; its three checks were done by hand.
7. Memspec promote PR into the team store: not done this cycle. The cycle's fact goes to local scratch (scope kvart) only.
8. Chrome extension not connected; QA ran on the skill's headless fallback with a throwaway script under `frontend/e2e/.runtime/`.
9. No multi-agent workflow: one-line fix, the standing ultracode opt-in carves out trivial edits.
10. macOS tooling gaps hit twice: no `timeout` (use the tool's cap or install coreutils), and `git stash` refuses intent-to-add files (use a file copy for negative test runs).
11. e2e from a worktree needs `COMPOSE_PROJECT_NAME=kvart` to reuse the primary postgres on :5432 and a copy of `frontend/e2e/.runtime/encryption.key`; neither is documented in `frontend/e2e/README.md`.

## Candidate ticket 2

Auto-pay label vs timers (MONEY): the settings hint says vendor auto-pay is not live while the daily timer acts on the stored flag; prod has one HOA with the flag on (0 payments so far). Needs an owner decision (label or behaviour; oldest-vs-newest settlement) before it becomes a ticket.
