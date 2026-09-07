# 0003. The merge gate is a cross-vendor, non-inheriting review, verified before action

- Status: accepted
- Date: 2026-08-08 (gate mandatory); 2026-08-19 (three axes); 2026-09-01 (security side-pass); 2026-09-04 (two backends, hard-fail)
- Deciders: the operator

## Context

One model family shares its blind spots with itself, and a reviewer that inherits the
author's session inherits the author's framing. Measured: the authoring model found 0 of 10
defects a fresh reviewer found 4 of. In one four-tool study 93.4 % of issues were caught by
exactly one tool.

## Decision

No push containing code changes and no PR until a review of the cumulative diff has run that
is (a) by a different vendor's model, (b) without the authoring session's context, and (c)
treated as a hypothesis set whose CRITICAL and SERIOUS claims are verified against code before
anyone acts. In addition: a blind security-only side-pass (same vendor allowed, additive only),
a scanner tier, and a browser QA pass on touched UI. Two cross-vendor backends; either
satisfies the axis; if all are unreachable the gate FAILS and nothing is pushed. Docs-only
commits are exempt unless they encode a security rule or a data-model decision. A review's own
fixes do not trigger a re-run.

## Consequences

- Positive: real defects that green tests and lint passed, including one against the author's
  own ticket scoping on a money path.
- Cost: 7 to 20 minutes per turn; a second vendor's account and credentials; the discipline
  to prove the reviewer ran (probe plus wall-clock) every time.
- Follow-ups: extend cross-vendor to the builder tier for lights-out operation; an F1
  benchmark set to score the reviewer and choose models on data.

## Alternatives rejected

- Same-vendor second opinion: measured blind.
- Silent degrade when the cross-vendor backend is down: turns a review failure into a false
  pass; the wrapper did exactly that twice before it was fixed.

## Evidence

- `docs/06-verify-gate.md`; `evidence/kvart-dogfood-cycle-2.md`; `evidence/kvart-head-hands-trial-report.md`.
