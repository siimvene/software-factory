# 0001. Adopt a standard; do not build a harness

- Status: accepted
- Date: 2026-09-04
- Deciders: the operator (architect role)

## Context

The first design for the legacy core built a standalone harness: its own gate set, module map,
spec template and memory topology, in parallel to an organisational standard that already
shipped an agent contract, a repository context standard with a team-context layer, a sandbox
template with an enforced egress gateway, a cross-vendor review plugin, spec retro-generation
and spec update skills, and rule packs.

## Decision

Every generic mechanism comes from the standard. Only the system-specific pieces are built
locally: the verification net for the specific core, its money tiering, its layering rules,
its stack's rule pack. Where no standard exists, this repository's templates and the named
third-party tools are the minimum, and they are adopted as they are, not re-implemented.

## Consequences

- Positive: one design version discarded instead of two parallel stacks maintained; every
  team that adopts the standard benefits from deltas folded upstream.
- Cost: adopting a standard onto a legacy system exposes the standard's assumptions (a healthy
  repo, a worktree-friendly sandbox, a credential that exists). Each mismatch is a finding to
  report upstream, not a reason to fork.
- Follow-ups: the deltas found (evals on agent config, security at the ticket stage, control
  bands for maintenance, managed settings plus scoped identity) go to the standard.

## Alternatives rejected

- Keep the standalone harness: duplicates maintained forever, no amortisation across teams.
- Fork the standard: same cost, plus drift.

## Evidence

- `docs/09-legacy-adoption.md`; `STATUS.md`, the legacy-core rows (verification net, money tiering, layering as lint).
