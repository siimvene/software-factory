# Changelog

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
