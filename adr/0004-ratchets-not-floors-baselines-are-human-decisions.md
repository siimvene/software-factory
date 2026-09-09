# 0004. Ratchets, not floors; baselines are a person's reviewed commit

- Status: accepted
- Date: 2026-09-04
- Deciders: the operator

## Context

A quality floor is negotiated once and then argued down. An agent under pressure to make a
gate pass will edit the policy if it can. On adoption day every real codebase carries debt that
cannot be cleared before the first turn.

## Decision

Every structural gate is a ratchet: a baseline records the debt present on adoption day, keyed
by site, and the gate fails on new debt or on baselined debt that got worse. The gate names the
file, the line and the fix, and refuses to say how to make the baseline accept the site. Editing
the policy, the baselines or the hooks is blocked for agents by a pre-tool guard, and loosening
a baseline is a person's reviewed commit that names what it accepts and why. Adopting the gate
onto a newer main is one deliberate re-cut by a person, recording main's real day-one debt.

## Consequences

- Positive: day one is green, drift is caught by name, and the guard held against its own
  operator.
- Cost: a red gate on pre-existing code blocks a feature branch until a person decides;
  bootstrap failures must be reported separately from feature failures so they are neither
  hidden nor dismissed.
- Follow-ups: an accept path for clones in changed lines that are import blocks (upstream).
- Follow-up (2026-09-09, measured on kvart #33 and #36): the CI gate runs the ratchets in
  strict mode, which requires the baseline to be tightened in the same PR whenever a diff
  improves the number, and the agent guard refuses that write by design. Every improving PR
  from an agent therefore needs a person's commit; two were made by hand in one day.
- Decided (2026-09-09 evening, the operator): option (b). The guard permits a baseline write
  that only lowers a number and keeps refusing every other write to the policy, the baselines
  and the hooks. Loosening stays a person's reviewed commit. Rejected: (a) CI tightens the
  baseline on merge and strict mode checks "not looser than the default branch", which moves
  the number out of the PR that earned it; (c) one human commit per improving PR, measured as
  four hand commits in one day on kvart. What the day's evidence separated first: of the seven
  baseline collisions on 2026-09-09, five were a diff bug (the ratchet diffed against the tip of
  the default branch instead of the merge base, fixed in kvart #41) and two were the real
  deadlock, the last one at 18:25Z on kvart #43 (baseline 11.93 % recorded, 11.92 % measured
  after #42 merged, strict mode wants an exact match) `[measured 2026-09-09]`. The check for
  (b): the guard's own planted cases, one lowering write that passes and one raising write that
  is refused, run in CI on the gate's repository.

## Alternatives rejected

- Thresholds an agent may raise with justification: the justification is always available.
- Floors set at the current value: the value drifts down with every accepted exception.

## Evidence

- `docs/05-sensor-stack.md`; `case-studies/kvart-head-hands-trial.md`, "the complexity gate,
  and a correction".

## Implementation note (2026-09-09, late evening)

Option (b) shipped as `--tighten` in the ratchet engine (fork PR #1, vendored into the
reference implementation by #45). The rewrite refuses to run whenever it would accept
anything new or worse, whenever the target file carries no recorded provenance (so a flag
or a config cannot point it at a settings file), under provenance drift, and for a run
scoped to a subset of files. The guard's regex did not change: it still refuses the
accept-debt command and every edit to policy paths, and lets `--tighten` through. Two
gates whose ratchet runs the other way, the inventory and the public API surface, where a
vanished entry is the failure, do not offer it; the blind security pass caught the first
draft offering it there. Planted cases live in the engine's own suites: the lowering write
that passes, the raising write that is refused with the file byte-identical `[measured 2026-09-09]`.
