# kvart dogfood, cycle 2 (2026-09-07)

> Source: the cycle-2 report written into the PM workspace's outputs folder at the end of the run, 2026-09-07.
> Copied near-verbatim, anonymised.

# The group SDLC dogfood on kvart — cycle 2 report (2026-09-07)

Ticket: the ticket file in the PM workspace, `payments-and-bank / 01 - Vendor auto-pay - retire the Enable Banking path`
Code PR: siimvene/kvart#18 (3 commits, `d830d406` → `54e93ba1`, +121/−679)
Sister spec PR: siimvene/kvart-team-context#5
Both open at 04:13; owner merges, then deploy (backend restart, two prod one-offs).

## Wall-clock per stage

| Stage | Start | End | Elapsed | Notes |
|---|---|---|---|---|
| PM: investigate the finding (code, prod DB, prod logs, audit trail) | 03:25 | 03:45 | ~20 min | corrected the premise: section invisible since 05-14, flag API-writable, initiation cannot complete unattended |
| PM: rail decision with Siim (Enable Banking is a write-off) | 03:45 | 03:50 | ~5 min | reframed the ticket from "fix the label" to "retire the path" |
| PM: draft ticket, self-score | 03:50 | 03:53:31 | ~4 min | 93/100 |
| Dev: worktree + venv, read the touched surface | 03:53:31 | 03:55 | ~2 min | |
| Dev: backend lane (principal) + frontend lane (Opus agent, disjoint files) in parallel | 03:55 | 03:58 | ~3 min | agent: 20 unit tests green, eslint clean, 89k tokens, 118 s |
| Dev: e2e (new fence + smoke) | 03:57:13 | 03:57:33 | 19 s | |
| Gate: scanner tier | 03:58 | 03:59 | ~1 min | 515 findings, identical to the cycle-1 baseline |
| Gate: blind security side-agent (Opus, non-inheriting) | 03:58 | 04:02 | 3 min 25 s | 2 LOW + 1 INFO, all verified, all fixed (commit 2); 110k tokens, 32 calls |
| Gate: Codex cross-vendor review | 03:57:47 | 04:07:35 | 9 min 48 s | 1 HIGH + 1 MEDIUM + 1 LOW; HIGH and MEDIUM verified and fixed (commit 3) |
| QA (`/qa`, headless, 7 surfaces, settings page exercised, legacy PUT negative) | 03:59 | 04:02 | ~3 min | no new findings |
| Commit 1 (retirement) | 03:58 | | | |
| Fix pass for the security findings, commit 2 | 04:02 | 04:05 | ~3 min | |
| Fix pass for the Codex HIGH (restore the poller) + MEDIUM (Wave 2 doc), commit 3 | 04:08 | 04:12 | ~4 min | one test needed its datetime import back |
| Push + PR #18 | 04:12:29 | | | |
| Sister spec PR #5 | 04:12:29 | 04:13 | <1 min | |
| **Dev hat on → code PR open** | 03:53:31 | 04:12:29 | **18 min 58 s** | Codex review is 52% of it; the review-driven fix passes 37% |
| (idle: waiting for the owner) | 04:14 | 09:39 | 5 h 25 min | not counted below |
| Owner merge (both PRs, on request) + worktree cleanup | 09:39 | 09:41 | ~2 min | |
| Pre-deploy gate (smoke + the settings fence, on merged main) | 09:41:46 | 09:42:04 | 17 s | 2/2 green |
| Deploy (pull, API restart, installer prunes the auto-pay timer, prod row reset, frontend build + restart) | 09:42:16 | 09:43:08 | 52 s | prod 98dbd711 → 736b770b, no migration, no dependency change |
| Prod verification (HEAD, bundle grep, services, timers, API journal, poller's next tick) | 09:43 | 09:47 | ~4 min | |
| **Dev hat on → live in prod, excluding the idle wait** | | | **~27 min** | |

Tokens: security agent 110,339; frontend agent 89,774. The principal is not instrumented.

## What the gate caught (the point of the exercise)

- **Codex HIGH, real.** My ticket had scoped the 15-minute poller out with the auto-pay. Nothing in the web UI calls the per-invoice status route, so an abandoned or bank-rejected manual payment would have stayed `initiated` forever and blocked every retry. Fixed by keeping the poller; the ticket's AC was corrected in place and marked as revised during the gate. A single-vendor review by the author's own model would likely have accepted the author's scoping. This is the cross-vendor axis earning its keep.
- **Codex MEDIUM, real.** The Wave 2 plan pseudocode still keyed on `auto_pay_vendors`, and prod carries a stale `true`; a literal Wave 2 implementation would have auto-activated gateway payments with no fresh consent. Doc fixed; the deploy resets the row.
- **Security LOW ×2, real.** The timer installer never disabled removed units (would have failed every 15 minutes on prod); the inline status route skipped the dedup key the bank-statement importer relies on. Both fixed.
- **Scanner:** nothing new. **QA:** nothing new.

## Skipped or shortcut steps

1. PM and dev hats in one session again.
2. `Features/` still absent; specs + code + prod investigation were the source.
3. `update-specs-for-commits` and `check-specs.py` still not installed; sister spec hand-edited, checks by hand.
4. No memspec promote PR this cycle either; local scratch only.
5. Headless QA fallback (no Chrome extension).
6. Consort not re-run after the review-driven fixes (allowed by the no-re-run rule); the restored poller is the previously reviewed code returning unchanged.
7. New this cycle: the `git stash` and `timeout` gaps from cycle 1 were avoided by design; the worktree Bash guard still cost ~6 refused commands (compound commands, heredocs mentioning git).

## Candidate ticket 3

Either the deploy of #18 as its own tracked step (backend restart + prune the timer + reset the prod row), or the oldest-vs-newest settlement question in bank matching, which nobody has verified yet.
