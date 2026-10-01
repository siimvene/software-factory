# 0005. Humans approve and merge; they never author. Hand-written code is an incident

- Status: accepted for the reference implementation; proposed for organisations
- Date: 2026-09-07
- Deciders: the operator

## Context

A factory whose output is partly hand-written cannot measure itself: the cost per feature, the
reviewer's F1 and the revert rate all mix two populations. And an engineer who hand-writes
features competes with agents and loses, while the factory never learns why it could not do
the work.

## Decision

Every commit carries an agent attribution trailer and a session link. A pre-receive or
branch-protection check rejects commits without provenance. Human identities approve and
merge, never author. Hand-written code is not forbidden; it is an incident: a logged override
with a post-mortem asking why the factory could not do it, feeding the backlog. Metric:
hand-written lines per week, target zero, next to cost per merged feature.

## Consequences

- Positive: clean populations for every metric; every gap in the factory becomes a ticket.
- Cost: a 3 a.m. hotfix carries paperwork; the engineer role changes to operator, module owner
  and evidence reader, and the readiness gate is to ship one feature by operating agents end to
  end.
- Follow-ups: decide whether overrides need a named approver or only the incident log.

## Alternatives rejected

- Mixed authorship with a percentage target: unmeasurable and unenforceable.

## Evidence

- `docs/07-roles-and-authority.md`, "provenance". The reference product already carries the
  trailer on every commit.
