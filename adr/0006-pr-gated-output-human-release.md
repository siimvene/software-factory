# 0006. PR-gated output; production release stays human; delegation is earned and revocable

- Status: accepted (PR gate, human release); proposed (delegated merge); one incident recorded (2026-09-09)
- Date: 2026-09-05
- Deciders: the operator, after an independent critic review of the proposal

## Context

Autonomy without a boundary is a crash factory. The evidence audit found no enforced
acceptance identity (approver, content hash, invalidation) in the existing tooling, generated
specs that document implementation rather than intent, and a spec that contradicted itself on
a business rule.

## Decision

Agent output stops at a PR. Merge is a human decision on evidence; production release is a
separate human authority. Money, tenant, identity and migration changes always require a
named-human outcome sign-off. Delegating the merge decision for a narrowly qualified recurring
pattern to PM-final acceptance is allowed only after a manual acceptance trial on one real
feature, with an engineering owner approving the pattern, expiry and revocation, protected
checks, and acceptance bound to the exact integrated artifact. Any escaped defect or
approval-integrity failure suspends delegation.

## Consequences

- Positive: blast radius stays bounded while the metrics that would justify widening it are
  collected.
- Cost: humans remain in the loop at merge; the throughput ceiling is human evidence-reading
  capacity, which is why humans must read evidence, not code.
- Follow-ups: the acceptance-identity mechanism; the first qualified pattern.

## Incident (2026-09-09) and what it decided

kvart #44, a loop-infrastructure PR, was merged at 18:34Z by the operator agent running the
owner's `gh` login, because the previous session's handoff note said "post the green line and
merge" `[measured 2026-09-09]`. The forge records the owner as the merger; nothing in the
ledger distinguishes that merge from a human decision on evidence. That is the
approval-integrity failure this decision names, and it happened without any gate refusing it:
branch protection checks the identity, and the identity was the owner's.

Decided by the operator the same evening:

- The loop does not merge. Merges return to the owner. A handoff may instruct a verify,
  never a merge; the handoff template and the operating contract carry that line.
- The first candidate for a qualified class stays "a loop-infrastructure PR after green", and
  it may be delegated only under the bot identity's own name, so every such merge is
  attributable, with the expiry and revocation above. Until the bot can merge under the
  ruleset as itself, the class does not exist.
- The check: a weekly query of merges by identity. A merge by the owner's identity from an
  agent session is the incident; the count's target is zero, next to hand-written lines.

## Alternatives rejected

- Immediate PM repository authority: transfers unresolved risk.
- Letting the operator agent merge green infrastructure PRs under the owner's login because
  the owner would have merged them anyway: removes the only evidence that a human decided.
- No change: leaves the acceptance gap.
- A governance programme before proving PM acceptance is useful: rejected by the critic as
  designing maturity before proving value.

## Evidence

- `docs/07-roles-and-authority.md`, "PM acceptance before PR-gate delegation".

## Open reference for the delegated-merge trial (2026-09-16, not decided)

An internal-systems diagram of OpenAI's own loop (sourced from OpenAI engineers, via Gergely
Orosz, 2026-09-15) shows a concrete shape for the narrowly qualified pattern this decision
already leaves room for: a low-risk change goes straight from agent review to an agent-babysat,
feature-flagged deploy with no per-change human wait, backstopped by two agents this design does
not yet have, a regression detector and an incident responder, both with a cheap rollback path.
Logged as two proposed rows in `STATUS.md` (production-feedback agents; risk-tiered deploy
autonomy). Read together: the missing piece is not appetite for delegation, which this decision
already grants a path to, it is the continuous production safety net that would make removing
the per-change wait a bounded bet rather than a wider one. Sequence the safety net first.
