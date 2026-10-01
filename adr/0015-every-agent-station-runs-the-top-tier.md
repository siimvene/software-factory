# 0015. Every agent station runs the top tier

- **Status:** accepted for the reference implementation
- **Date:** 2026-09-29
- **Deciders:** the operator
- **Supersedes:** the per-task worker-tier routing in `docs/07-roles-and-authority.md`
  (mid tier builds, top tier debugs and verifies), in force 2026-08-11 to 2026-09-29

## Context

The routing rule it replaces defaulted BUILD stations to the mid tier and reserved the top tier
for debugging with an unknown root cause, security side-agents, adversarial verification and
fixes of CRITICAL and SERIOUS findings. Its evidence was six mid-tier build cycles with no
regression attributed to the tier, at about half the bill `[measured 2026-09-08..09]`.

Two things weaken that evidence:

- "No regression attributed to the tier" is the absence of a signal at n=6, with no
  controlled comparison. The sensor trial built one brief three times on the top tier: two runs
  that differed in nothing the builder used were 35 % apart on cost, and the trial concluded
  that one run per arm cannot separate an effect from variance `[measured 2026-09-29]`. Six
  uncontrolled cycles cannot see a tier effect either, in either direction.
- Tiering is a decision per station, and the decision leaked. A model alias is a per-config-
  directory setting; about 11,000 subagent calls ran on the wrong tier for almost four weeks
  before the served-model audit found it `[measured 2026-09-08]`.

## Decision

Every agent station runs the top tier: builders, fixers, scouts, research, security
side-agents. Reviewers and adversarial verifiers may run the reviewer model instead. No mid- or
low-tier stations. On the reference machine that is Opus 5.5 for every station and Fable 5.1
as the reviewer option.

- The model is passed explicitly on every spawn; nothing inherits the session's model.
- Every config directory pins the alias: `ANTHROPIC_DEFAULT_OPUS_MODEL` and a
  `modelOverrides` entry map the bare alias to the pinned release, so an earlier release
  (distrusted for run-to-run variance) is never served by accident.
- Effort floor medium for every station. High for money paths, security, adversarial
  verification, fixes driven by review findings, and debugging with an unknown root cause. The
  orchestrating session runs high by default.
- Escalation stays by re-brief: a fresh station carrying the failed attempt's evidence, never
  the same brief retried.
- Cross-vendor consort reviewers are not stations and are unaffected.

## Consequences

- **Positive:** one routing predicate instead of a judgement per station. Checkable: the weekly
  routing audit reads the served model, and any station served by another model is a leak,
  target 0.
- **Cost:** the station bill roughly doubles against the mid-tier default
  `[measured 2026-09-08..09]`, so the payoff bar in `docs/10-measurement.md` (cost per commit
  under $8 list) is at risk and is re-measured, not assumed. The operator's stated position:
  correctness and coverage are the constraint, not token cost.
- **Follow-ups:** re-measure cost per commit over the first full week under this rule
  (operator); if a tier effect is ever measured at a sample size that can see it, it reopens
  this decision.

## Alternatives rejected

- Per-task tiering (the superseded rule): saves about half the station bill for a quality
  difference nobody can measure at current volume, and adds a routing surface that has
  already leaked once.
- The reviewer model at every station: it is the scarcer budget (a monthly spend cap was hit
  on 2026-09-23 `[measured 2026-09-23]`), and a station that cannot start is worse than one
  on the top tier.

## Evidence

- `docs/07-roles-and-authority.md`, head and hands; `docs/10-measurement.md`, the payoff bar
  and the routing audit; `evidence/kvart-sensor-trial-2026-09-29.md`, run-to-run spread.
