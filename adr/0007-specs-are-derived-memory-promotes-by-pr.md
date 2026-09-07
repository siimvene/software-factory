# 0007. Specs are derived from merged code; durable memory reaches the team store by PR only

- Status: accepted
- Date: 2026-09-07
- Deciders: the operator

## Context

Hand-maintained specs drift; the reference product had 100+ design documents and a rule file
describing an authentication model retired months earlier. A memory store inside the code repo
mixes disposable scratch with durable knowledge and gives every session write access to what
every other session reads.

## Decision

Current-state specs live in a team-context repo, are bootstrapped by retro-generation over the
code with owner review of the candidate table, and are updated only by a sister PR on every
behaviour-changing code PR. Hand edits are forbidden. The code repo carries no memory store;
it binds read-only to the team store. Agents write to local scratch at the moment of
discovery; durable knowledge travels by a batched, human-reviewed promote PR. Proposed,
implemented and released state are kept separate: tickets are desired state, specs are
implemented state.

## Consequences

- Positive: the LEARN edge is live from the first turn; the bootstrap doubles as an audit
  (the findings file became the ticket backlog).
- Cost: a day of bootstrap; promote-PR friction. Both dogfood cycles skipped the promote PR,
  which is a measured finding about the friction, not a reason to drop the mechanism.
- Follow-ups: install the spec-update and spec-check skills so the sister PR is generated,
  not hand-edited; measure whether a solo owner keeps writing memory under promote-PR friction.

## Alternatives rejected

- Hand-maintained specs: drift, measured.
- Direct writes to the team store: no review, and every session's scratch pollutes the shared
  truth.

## Evidence

- `docs/04-knowledge-plane.md`; `case-studies/kvart-reference-implementation.md`, "Day 1".
