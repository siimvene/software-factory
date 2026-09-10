# Changelog

## 0.2.6 (2026-09-10)

The spec becomes a VERIFY input, proposed.

- `adr/0009`: the spec is a gate input; scope drift is a finding with its own disposition.
  Context from cycle 4: the panels ran before the decisions existed, the scope question came
  from code and was adjudicated by the authoring session alone, the pre-build spec and its
  delta were both unmerged; cycle 5's delta open at handoff. Four alternatives weighed,
  including the one that looked obvious (compare with the ticket text) and the one that looked
  disciplined (fold every decision in first); both rejected with reasons.
- `docs/06-verify-gate.md`: "Spec conformance" section: injected spec pack to every leg, the
  scope-drift class both ways, REFINE-SPEC, the delta as a receipt-checked pre-push gate, and
  the test the class must pass before it is trusted.
- `docs/02-loop.md`: REFINE-SPEC in the disposition list; LEARN item 1 names the receipt.
- `docs/03-operating-contract.md`: §11, a decision that changes behaviour also goes into the
  delta; enforcement table row.
- `docs/16-inventory.md`, `STATUS.md`, `adr/README.md`: the rows.

## 0.2.5 (2026-09-10)

Sensor 2 changes tool: chisle replaces ponytail on the reference implementation, same ladder.

- `docs/05-sensor-stack.md`: Layer 2 names chisle, what it adds (prose ruleset, tool-output
  elision with its kill switch), why the swap (the vendor's 20-task comparison), the caveats
  (hooks read in full, a tag pin rather than a commit pin, elision as a possible new failure
  class); the wired-where row.
- `evidence/field-evidence.md`: section 5a, the chisle record with the comparison table and the
  pre-adoption audit; section 5 stays as the dated ponytail record.
- `docs/16-inventory.md`, `README.md`, `STATUS.md`: the Sensor 2 rows and the picture.
- `WRITING.md`: chisle joins the nameable tools.
- `templates/ticket.md`: "Escalation triggers" section. Without an explicit list of escalate-when
  conditions the agent infers its own bail-out criteria; the section makes them a first-class
  part of the spec `[field: Ichigo, "Harness Engineering", 2026-08-29]`.
- `docs/10-measurement.md`: headline ratio, accepted outputs over human review minutes. The
  numerator is merged PRs a human said yes to; the denominator is review-active minutes with
  idle wait excluded. The per-turn numbers diagnose; this ratio is the mandate signal.
- Merge note: a parallel session published the tool swap plus the two items above as a second
  "0.2.4" on 2026-09-10 morning; that entry is folded here, and 0.2.4 stays the browser QA
  runtime.

## 0.2.4 (2026-09-10)

The browser QA runtime, after evaluating the Playwright CLI against the kvart stack.

- `adr/0008`: the browser QA pass drives a CLI, not a protocol server or a browser extension;
  one session per persona, state saved once and restored; evidence on disk, a few lines in
  context; a missing runtime stops the pass instead of a hand-written script; the skill is
  tracked so a station worktree has it.
- `docs/06-verify-gate.md`: the runtime paragraph under the receipt gates, with the shakedown.
- `docs/05-sensor-stack.md`, `docs/15-design-system.md`: the row notes; the page tree the runtime
  writes is the input for the still-designed patterns check.
- `docs/13-failure-catalogue.md`: three rows (a gitignored skill is absent from every worktree;
  browser state saved during the SPA callback; the 0-byte auto-named page tree).
- `STATUS.md`: Browser QA pass row carries the runtime, the shakedown, the cold rehearsal and the
  gate on the skill itself (security pass, two-vendor panel, dispositions).

## 0.2.3 (2026-09-09, evening)

The evening's eight loop-infrastructure PRs on kvart, and two decisions the day forced.

- `adr/0004`: decided, option (b): the guard permits a baseline write that only lowers a
  number. The day's seven collisions split into five from a merge-base diff bug and two real
  deadlocks.
- `adr/0006`: incident recorded, an agent merged a green PR under the owner's login on a
  handoff's instruction; decided that the loop does not merge and a handoff never instructs
  one; the qualified class waits for the bot identity to merge as itself.
- `docs/02-loop.md`: receipt-checked pre-push gates as a VERIFY step (browser pass measured,
  static analysis designed); the merge line; cycle 3 and cycle 4 rows in the cost table.
- `docs/05-sensor-stack.md`, `docs/06-verify-gate.md`: the receipt pattern, the rehearse-the-
  blocked-direction rule with its three defects, the strict-mode base_ref hardening, the
  worktree scanner degradation.
- `docs/07-roles-and-authority.md`: the measured worker-tier routing rule and the served-model
  audit (alias leak).
- `docs/14-pm-surface.md`: the tracker is real; the status-line shortcut is a dated past state.
- `docs/03-operating-contract.md`: claim a broken shared gate before fixing it; commit the real
  change before a throwaway commit; a handoff instructs a verify, never a merge.
- `docs/10-measurement.md`: factory-on-itself share (8 of 13 merges on 2026-09-09).
- `docs/13-failure-catalogue.md`: eight rows (introducing PR cannot exercise itself, two
  sessions on one red gate, the probe that swept an uncommitted fix, stale lock and a stale
  shared checkout, a baseline staged but not committed, a gate that cannot fail on bash 3.2,
  base_ref = HEAD, the alias leak).
- `templates/handoff.md`: the merge line.
- `STATUS.md`: static-analysis receipt gate (designed), worker-tier routing, the merge
  incident on the ruleset row, the factory-on-itself metric, the scanner caveat.

## 0.2.2 (2026-09-09)

Cycle 4 on kvart: first batch (an epic with four stories) through the loop with three parallel
stations against a written contract. What it exposed, and where it landed:

- `docs/03-operating-contract.md` §11: agent-surfaced decisions (questions, dismissals,
  deviations) go to the escalation channel and the ledger, with default and deadline; labels
  on the ticket; write-back by hand until automated. Recorded after a measured lapse.
- `docs/13-failure-catalogue.md`: nine rows (queued canvas station, worktree provisioning
  drift, station wiped its venv, brief-planted field name, strict ratchet vs guard deadlock,
  impact-slice coverage floor, two PRs tightening one baseline, a false "suite is red", a
  review finding that contradicts the spec).
- `adr/0004`: follow-up on strict mode versus the agent guard, three options, one recommended.
- `STATUS.md`: escalation row updated; two new measured rows (contract-first parallel
  stations; fix station after the panel).

## 0.2.1 (2026-09-07)

Downstream fixes referenced. The design named the sensors; this records what broke in them on
the first full day and where each fix landed.

- `docs/05-sensor-stack.md`: four new layer-3 rules (a Stop hook reports a failure set once, a
  formatter pass is not a change, a gate that cannot fail is not a gate, a pre-push gate must
  read the ref list), the fork-and-PR path for a third party's tool, and the layer-4 Stop hook
  replaced by a check that blocks once, with its planted cases.
- `case-studies/kvart-reference-implementation.md`: the afternoon section, kvart #22 to #24,
  the worktree and branch pile with its root cause.
- `STATUS.md`: the ratchet and architecture rows carry the fix references; the pre-push and
  worktree rows carry the open defect and the pile.

## 0.2.0 (2026-09-07)

Coverage of the surfaces the first cut only named.

- `docs/14-pm-surface.md`: the PM workspace, a catalogue of its skills, the readiness rubric,
  the intake-to-ticket pipeline and the proposed/implemented/released boundary.
- `docs/15-design-system.md`: the design-standards repo as a knowledge-plane layer.
- `docs/16-inventory.md`: every mechanism mapped to what provides it today and what an adopter
  without an organisational standard must build.
- `docs/17-onboarding.md`: the Day 1 runbook (team-context repo, standard adoption, instruction
  split, memory move, three-mode spec retro-generation with owner review, ADR candidate table
  and mining, PM workspace, design system), with the kvart numbers.
- `templates/pm-skill.md`: a generic skill skeleton.
- `STATUS.md` and the README reading order extended.

## 0.1.1 (2026-09-07)

Visuals. The design had none: every mechanism was prose and tables only.

- `README.md`: the delivery line end to end, 9 layers in 3 frames (ergonomics, gates,
  after the PR), with an index table naming what each layer refuses and its evidence class.
- `docs/02-loop.md`: the loop redrawn with the knowledge plane at the centre, replacing the
  ASCII sketch that showed LEARN returning straight to SPEC without the hub. Both write-backs
  are now edges, and the memory arrow is drawn dashed because it fired zero times in two
  measured cycles.
- `docs/05-sensor-stack.md`: where each sensor fires inside one agent turn, plus a table of
  which checks are wired on kvart and on the legacy core.

Diagrams are mermaid so they render on the forge, diff as text and can be adapted by a reader.
Fill encodes the evidence class from `WRITING.md`, never severity. `STATUS.md` stays the ledger.

## 0.1.0 (2026-09-07)

First consolidation. Derived from:

- the kvart dogfood, 2026-09-07: Day 1 bootstrap, cycle 1 (public-route fix), cycle 2
  (retire a payment path), the sensor-stack wiring;
- the head-and-hands harness trial on kvart, 2026-09-05;
- the legacy-core flywheel work, 2026-09-04 to 09-07: design v0 and re-base, turn 0 adoption,
  turn 1 verification net, money tiering, ratchets, layering gate, complexity ratchet, sandbox
  boot;
- the operator contract and its rule set as of 2026-09-07;
- the planning-to-validation evidence audit and proposal v3, 2026-09-05;
- the measurement baseline and the scaling analysis, 2026-09-07.

Contents: 14 design documents, 3 case studies, 4 evidence files, 8 templates, 7 decision
records, the status ledger.
