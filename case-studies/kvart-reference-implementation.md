# Case study: kvart as the reference implementation

kvart is an apartment-association management SaaS: a billing engine held to cent-for-cent
parity with the incumbent, accounting sync, bank integrations, national eID authentication,
row-level tenant isolation enforced in the database, a web and a mobile client, 4 locales. One
founder, no VC. It is the place where the loop was first run for real, and the numbers in this
design are its numbers.

This case study covers 2026-09-05 to 09-07: the harness trial (separately in
[kvart-head-hands-trial.md](kvart-head-hands-trial.md)), Day 1 (bootstrap), cycles 1 and 2,
and the sensor-stack wiring. Source reports are in [../evidence/](../evidence/).

## Starting state (2026-09-05)

- A broad production codebase (~200 backend routes, 187 migrations, ~250 features), production
  on a single VM, real users, money paths live.
- Rich design documentation (100+ documents) but no current-state specs, no decision records,
  and no ticket stage: work started from a backlog file that was stale toward done.
- A memory store of ~317 records inside the code repo.
- An operator contract (verification discipline, consort gate, delegation rules) already in
  force for every session, and the cross-vendor review gate already the habit before any push.
- Quality ratchets existed on a diverged branch, not on main.

The trial on 2026-09-05 showed the cost of no ticket stage: with no PM-authored acceptance
criteria, the building agent wrote its own criteria and later rewrote them to fit what it
built. That observation is the origin of ADR 0001 in the team-context repo.

## Day 1: bootstrap (2026-09-07, one session)

Decision: kvart becomes the guinea pig for the group's agentic SDLC. Build the team layer and
the bootstrap, change no product code.

| Step | What | Result |
|---|---|---|
| Team-context repo | created, private; front-door instructions, CODEOWNERS, ADRs 0001 (solo dogfood, shortcuts named) and 0002 (bootstrap before the first ticket) | branch protection refused on the plan (HTTP 403): merge gate is a habit, recorded in ADR 0001 |
| Memory store move | the 316 active records moved into the team-context repo with history (subtree) | code repo binds read-only; verified `team [ro] 316 items` |
| Context standard at L0 | sentinel in the agent instructions, lock file, memory pointer, seeded architecture, manifest and agent-memory docs, ADR 0001 in the code repo | the docs-lint workflow calls a private reusable workflow and was disabled; L2 gate, repo at L0 |
| PM workspace | copied from the template; pointers filled; no ticket tracker | template skills hardcode organisation specifics and reference a missing style file |
| Design standards repo | tokens, 28 patterns, 31 components, two design handoff bundles recovered from ignored zips, 20 divergences documented | |
| Specs | retro-generation by hand (skill not installed): 3 feature maps → 264 candidate slugs → owner review → 20 parallel writers | **247 spec pairs, 20 subdomains, 5 NOT IMPLEMENTED**, every folder passing the checker |
| ADRs | 13 repo-level from a candidate table of 30; 8 team-level | every evidence path verified |
| Findings file | defects, dead surface, docs-behind-code from the writers' verified notes | the Day 2 ticket backlog |
| Incident | the primary checkout had `core.bare=true`, set by a gate branch's own pre-commit fixture run | reset, verified |

The most consequential finding was a rule file that loads into every session describing a
one-year web token, while the code had used 15-minute access plus role-tiered refresh since
2026-06-25. It was rewritten before any auth work.

The four docs-only PRs (team pointers, team ADRs, specs plus findings, repo ADRs) were merged
by the owner the same day after reading for business truth.

## Cycle 1: a one-line fix through the whole loop (2026-09-07, 02:40 to 03:19)

Ticket: the invited-board-member signing route was missing from the web public-route list;
invitees have no account, so they bounced to login. Root cause: the signing page and the
fraud-report page shipped in two commits and only the second got the allowlist arm.

| Stage | Elapsed | Note |
|---|---|---|
| PM: verify 3 candidates against code and prod; draft; self-score 94/100 | ~11 min | included a prod check on the payment flag (1 association on, 0 payments) |
| Dev: worktree, deps | ~1 min | 6 s and 1 s installs from shared caches |
| Dev: unit case red on the unfixed middleware | 30 s | exact wrong bounce asserted |
| Dev: one-line fix, 101/101 green, lint | 25 s | |
| Dev: browser spec, stack boot, pass; negative run with the fix reverted | ~4 min | lost one attempt to a missing `timeout` binary on macOS; `git stash` refused an intent-to-add file |
| Gate: scanners | <1 min | 515 pre-existing dependency CVEs, none from the diff |
| Gate: cross-vendor review | 7 min 06 s | 0 findings; reachability probe first |
| Gate: blind security side-pass | 2 min 53 s | 0 findings, 2 info; 113k tokens, 19 tool calls |
| QA: 10 surfaces headless | ~4 min | 0 CRITICAL/SERIOUS, 1 pre-existing MINOR |
| **Dev hat on → code PR open** | **12 min 11 s** | review is 58 % of it |
| Sister spec PR | 1 min 33 s | hand-edited |
| Owner merge, cleanup | ~4 min | |
| Pre-deploy gate, deploy, prod probe | 16 s, 39 s, <1 min | frontend build and restart only; no migration |
| **Dev hat on → live** | **~28 min** | |

Bonus finding, from the security side-pass and verified: the old login bounce put the signing
capability token into the `/login?redirect=` URL, which browser history and access logs
captured; the log scrubber only masked path-shaped tokens. The fix removed the leak.

Eleven shortcuts recorded (PM and dev hat in one session; a skill with a missing reference
file; specs standing in for a features folder; readiness self-scored; spec update and spec
checker not installed, done by hand; no promote PR; headless QA; no multi-agent workflow for a
one-liner; two macOS tooling gaps; undocumented worktree e2e needs). Each is in the report.

## Cycle 2: retire a money path (2026-09-07, 03:25 to 04:13, deployed 09:42)

Ticket started as "the settings hint says vendor auto-pay is not live while the timers act on
the flag". Twenty minutes of PM investigation (code, prod DB, prod logs, audit trail) corrected
the premise: the section had been invisible to every user since 2026-05-14 (capability
hardcoded false), the flag was API-writable by any board member, the aggregator's payment
initiation returns a payer-eID redirect so an unattended job cannot complete a payment, and it
had never initiated anything in prod. Owner decision in 5 minutes: the aggregator is a
write-off for payments; retire the path; vendor auto-pay returns on the direct gateways with a
new opt-in field.

| Stage | Elapsed | Note |
|---|---|---|
| PM: investigate, decide, draft, self-score 93/100 | ~29 min | |
| Dev: worktree, read the touched surface | ~2 min | |
| Dev: backend lane (principal) + frontend lane (subagent, disjoint files) | ~3 min | subagent: 20 unit tests green, 89k tokens, 118 s |
| Dev: e2e fence + smoke | 19 s | |
| Gate: scanners | ~1 min | identical to the cycle-1 baseline |
| Gate: blind security side-pass | 3 min 25 s | 2 LOW + 1 INFO, all verified, all fixed |
| Gate: cross-vendor review | 9 min 48 s | 1 HIGH + 1 MEDIUM + 1 LOW; HIGH and MEDIUM verified and fixed |
| QA: 7 surfaces, settings page exercised, legacy write path negative | ~3 min | nothing new |
| Fix passes, commits 2 and 3 | ~7 min | one test needed an import back |
| **Dev hat on → code PR open** | **18 min 58 s** | review 52 %, review-driven fixes 37 % |
| idle: owner asleep | 5 h 25 min | not counted |
| Owner merge, cleanup | ~2 min | |
| Pre-deploy gate, deploy | 17 s, 52 s | API restart, timer pruned, prod row reset, frontend rebuilt |
| Prod verification | ~4 min | services, bundle grep, timers, journal, poller's next tick |
| **Dev hat on → live, excluding idle** | **~27 min** | |

What the gate caught, and why it is the point of the exercise:

- **Cross-vendor HIGH, real.** The ticket had scoped the 15-minute status poller out with the
  auto-pay. Nothing in the web UI calls the per-invoice status route, so an abandoned or
  bank-rejected manual payment would have stayed `initiated` forever and blocked every retry.
  Restored. The acceptance criterion was corrected in place and marked revised during the gate.
  A same-vendor review by the author's own model would likely have accepted the author's
  scoping.
- **Cross-vendor MEDIUM, real.** The next-wave plan pseudocode still keyed on the retired flag,
  and prod carried a stale `true`; a literal implementation would have auto-activated gateway
  payments without fresh consent. Doc fixed; the deploy reset the row.
- **Security LOW ×2, real.** The timer installer never disabled removed units (would have
  failed every 15 minutes on prod); the inline status route skipped the dedup key the statement
  importer relies on.

Removed: the daily job and timer, two eligibility helpers, two settings API fields, a settings
section component, 4 locale keys × 4 languages, the disabled-switch tests. Kept unwritten: the
database column, to drop with the next-wave migration. Fence: a browser spec asserting the
section is gone. Diff +121/−679.

## The sensor stack wiring (2026-09-07, later session)

Merged as one PR (9 commits) after the owner's merge on request; nothing runs in production
(the image copies only source and migrations; every hook is a no-op where its binary is
absent).

- Quality ratchets vendored (6 gates green: doc-size, test-hygiene, escapes, conventions,
  duplication, complexity), baselines re-cut to main with 4 accepted sites named in the commit.
- Architecture diff tool with a layer declaration (entry → service → domain → models →
  foundation); 12 existing module-level crossings pinned; the real one is nine service modules
  lazy-importing an authorisation helper from the entry layer.
- The agent settings file is now tracked: PreToolUse guard, Stop gate then architecture diff,
  SessionStart snapshot, the YAGNI plugin with its marketplace source pinned. MCP servers for the
  orientation map and the architecture tool, PATH-prefixed launchers. Rule files for both.
- Gate on the PR itself: cross-vendor review 17 findings in 20 min 19 s, blind security
  side-pass 4 SERIOUS. Fixed: an argv injection via a changed path beginning with `-` (refusal
  exits 2 under the hook), a `MULTILINE` anchor baselining an empty-text site, MCP launcher PATH,
  the plugin source pin. Acknowledged: the PreToolUse guard is a speed bump; the control is
  branch protection. 11 product findings deferred upstream to the tool.
- **The guard is live and works.** After the merge it refused this agent's own baseline re-cut
  and a PR command whose body merely quoted the flag. Not routed around.
- Follow-up PR (config only): the walkers read nested worktrees under the repo and sent 3 of 6
  gates red in the primary checkout; fixed and proven with planted files.

## What the dogfood established

1. The loop runs end to end on a real product with real money paths at 12 to 19 minutes from
   dev hat on to PR open, and under 30 minutes to live, excluding waits on humans.
2. The cross-vendor, non-inheriting review found real defects that green tests and a same-vendor
   review would not have: one against the ticket's own scoping on a money path.
3. The bootstrap (specs, ADRs, team layer) is a day of work and doubles as an audit: the
   findings file became the backlog.
4. What a solo owner drops (promote PRs, separate PM and dev sessions, installed spec skills,
   branch protection) is the list of what a team must keep, and each is now a measured shortcut
   rather than an opinion.
5. The ratchet guard held against its own operator. That is the property a dark factory needs
   from every gate.

## Open at the end of the window

Owner decisions: settlement order in bank matching (oldest vs newest, unverified); the manual
pay button still on the retired aggregator until the next wave; a mobile redirect-host
allowlist; role-removal not revoking refresh tokens (documented gap); a person re-cutting the
complexity baseline after the exclude change; whether the plugin needs a real pin (fork or
vetted catalog) before use outside the dogfood.
