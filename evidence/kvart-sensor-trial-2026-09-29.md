# Sensor trial: orientation map, YAGNI ladder, architecture diff (kvart, 2026-09-29)

Goal: move sensors 1, 2 and 4 from `designed` towards `measured`. Five instruments, all run on
2026-09-29 against kvart at `eaac0496b` unless stated.

## 1. Orientation map (ripwire 0.4.0): index across worktrees

The MCP server (`ripwire --mcp`) was started in a detached worktree and queried with
`find_symbol` over stdio.

| Case | Expected | Observed |
|---|---|---|
| Symbol planted in the worktree before the server started | found | found, 0.0 s |
| The same symbol queried against the main checkout | not found | not found, 2.6 s |
| Symbol added while the server runs | found | found, 10.1 s (re-index) |
| Symbol deleted while the server runs | not found | not found, 0.9 s |
| Main checkout holding nested worktrees under `.claude/worktrees/` | same definition count as a clean tree | 2 and 2 |

A known symbol was found first, as the positive control. The index is per root, stays fresh
inside a session, and does not read nested worktrees `[measured 2026-09-29]`.

## 2. YAGNI ladder (chisle 3.0.0): install scope and output elision

**Install scope.** chisle was enabled in kvart's tracked settings but installed at project
scope, and a project-scope install is keyed to one exact directory. The install was recorded
for a scratchpad path only, so the main checkout and every worktree ran without it: no elision
in any kvart transcript after 2026-09-22, and a session's startup plugin list did not contain it
`[measured 2026-09-29]`. Fixed the same day: a user-scope install at the same pin (installed
commit `a5486fa112` equals the `v3.0.0` tag), the user-level switch set to off because the install
writes it as on for every repository, and the project's tracked settings switching it on. Checked
by the plugin list at session start: on in the main checkout, off in another repository, off where
a local settings file disables it. The blind security pass on this change caught the user-level
switch: the first cut had left chisle on in every repository.

**Elision audit.** Every kvart transcript on the reference machine (2,751 files):
- 67 elisions: 59 shell outputs, 7 memory searches, 1 tracker search.
- 4 candidate re-fetches by heuristic (the same command within the next three shell calls). All
  4 were read by hand and none was caused by an elision.
- 1 suspected silent loss: an orchestrator dumped six ticket briefs, 19 lines were elided, and
  its next turn said "full briefs captured" before it wrote builder prompts from them. Whether a
  missing line reached a prompt was not checked `[measured 2026-09-29]`.

## 3. Architecture diff (enola 0.4.19): backtest and live record

**Backtest.** For each of the 201 first-parent merges on main since the architecture config
landed (2026-09-16 to 2026-09-29), a baseline was pinned at the first parent and the merge was
graded with the Stop gate's policy (`--fail-on=layers,cycles,intent`) in a clean worktree.

| Result | Merges |
|---|---|
| clean | 199 |
| regression | 0 |
| incomparable: the merge changed the ignore globs (one also the extractor set) | 2 |

Median 8 s per merge. Positive control: a models to api import planted on the base exits 1 with
status `regression`. So no merge in 13 days introduced a provable layer, cycle or intent
regression, and the gate had nothing real to catch `[measured 2026-09-29]`.

**Live record.** The same period in the agent transcripts:
- 12 Stop-hook blocks. All 12 were false positives: a cycle between `frontend` and generated
  `frontend/.nuxt` (fixed in kvart #285), nested worktrees scanned as source, and one block in a
  session that had edited nothing.
- 10 did-not-run results, mostly exit 3 (baseline not comparable). The hook treats these as
  blocks, so each cost the agent one turn.

Every false block came from working-tree state that committed code does not have
`[measured 2026-09-29]`.

## 4. Controlled build: one brief, three runs, one variable each

KVART-256 slice 1: a new association role (`valitseja`) that reads what the board tier reads on
one association, has two write powers, and ends a management company's access with billing
effects. Seven numbered examples; the acceptance test must enumerate the app's routes. Auth,
tenant scoping and billing, about 1,000 to 1,500 changed lines.

Same base commit, same brief, same model (top tier, high effort), headless, solo (no subagents),
run one after another on one machine. Only the sensor configuration differed.

| Run | chisle | ripwire | Wall-clock | Tool calls | Cost (list) | Output tokens | Diff |
|---|---|---|---|---|---|---|---|
| r1 | on | on | 48 min | 138 | $19.53 | 103k | 12 files, +942 −17 |
| r2 | off | on | 50 min | 174 | $31.03 | 145k | 17 files, +1,447 −148 |
| r3 | on | off | 47 min | 172 | $26.30 | 134k | 20 files, +1,251 −44 |

- **ripwire was never called in r1, where it was available.** The headless builder did nearly
  all its work in the shell: 128 of 138 calls in r1, with 4 file reads and 0 searches through a
  tool. So r1 and r3 differ in a tool neither used. Their gap (cost 35 % apart, tool calls 25 %
  apart) is the run-to-run spread of identical work.
- **chisle's saving sits inside that spread.** r2, without it, cost more than both runs with
  it. But r2 was $4.73 above r3, less than the $6.77 between the two runs that differed in nothing
  used. One run per arm cannot separate the effect from variance.
- **The cheapest run redefined an acceptance example.** r1 answered 200 on three portfolio
  routes where example 3 required 403, and recorded the change as an assumption. r2 and r3
  returned 403. n = 1, and it is the failure mode the ladder's caveat names.
- **All three converged on the same design:** reads allowed by HTTP method, direct linking for
  bring-in, no migration. They also shared the spec's gaps.
- **Tests run.** r2 ran the full suite (12,759 passed; 26 environmental failures that pass on
  rerun). r3 ran 144 files and r1 ran 91.

**Review.** Two vendors on each diff (Codex, and Gemini through Pi), after all builds:

| Run | Codex | Gemini | Leg time |
|---|---|---|---|
| r1 | 8 (5 HIGH, 3 MEDIUM) | 1 HIGH | 457 s |
| r2 | 4 HIGH | 1 HIGH | 390 s |
| r3 | 7 HIGH | 1 HIGH | 521 s |

In r3 the Gemini leg made 0 tool calls, so it reviewed the diff without reading the repository.

- **Shared by all three runs, so a gap in the spec:**
  - The contract-end teardown deletes board roles that it cannot prove the company created.
    Both vendors raised it on every run.
  - Ordering between the new powers and the existing link writers.
  - No production caller for the grant. This is by design: a later slice owns the grant.
- **Specific to one run:**
  - r1: former staff whose membership is inactive keep their roles (both vendors).
  - r2: a person who is both valitseja and management staff loses the portfolio view.
  - r3: invoices can be left with no delivery route after contract end.
  - r3: a read on the billing routes creates default rows. r2's own report shows the same
    behaviour.
- **Unverified, shape shared by all three:** the role gate treats a mixed scope as authorised if
  any association in it is a valitseja read. Raised by one leg on r3 only; must be settled before
  any of the three becomes a pull request.

## What this measures, and what it does not

- Measured: ripwire's index across worktrees; chisle's install-scope failure and its elision
  record; enola's clean backtest and false-block record; the run-to-run spread of one
  top-tier build (about 35 % on cost).
- Not measured: an effect of chisle or ripwire on the quality or cost of a build. That needs
  several runs per arm, and for ripwire a builder that actually uses it (it appears in 1,176
  transcript files of interactive sessions; the headless builder never called it).
