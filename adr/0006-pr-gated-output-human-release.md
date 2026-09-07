# 0006. PR-gated output; production release stays human; delegation is earned and revocable

- Status: accepted (PR gate, human release); proposed (delegated merge)
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

## Alternatives rejected

- Immediate PM repository authority: transfers unresolved risk.
- No change: leaves the acceptance gap.
- A governance programme before proving PM acceptance is useful: rejected by the critic as
  designing maturity before proving value.

## Evidence

- `docs/07-roles-and-authority.md`, "PM acceptance before PR-gate delegation".
