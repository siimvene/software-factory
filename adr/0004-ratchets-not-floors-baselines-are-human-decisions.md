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
  from an agent therefore needs a person's commit; two were made by hand in one day. The
  decision this ADR does not yet make: (a) CI tightens the baseline on merge to the default
  branch and strict mode checks "not looser than the default branch"; (b) the guard permits
  writes that only lower a number and keeps refusing the rest; (c) keep one human commit per
  improving PR as the cost of the rule. (b) keeps the human at every loosening and removes the
  deadlock; it is the recommended option pending the operator's word.

## Alternatives rejected

- Thresholds an agent may raise with justification: the justification is always available.
- Floors set at the current value: the value drifts down with every accepted exception.

## Evidence

- `docs/05-sensor-stack.md`; `case-studies/kvart-head-hands-trial.md`, "the complexity gate,
  and a correction".
