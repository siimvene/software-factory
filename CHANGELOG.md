# Changelog

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
