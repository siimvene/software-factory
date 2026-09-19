# 0002. Mechanical sensors run before any inferential review

- Status: accepted
- Date: 2026-09-07
- Deciders: the operator

## Context

A cross-vendor model review is the most expensive step in a turn: 52 to 58 % of the dev-hat
wall-clock in the reference cycles. Some of what it finds (escapes, oversized functions,
copy-paste, layer crossings, uncovered changed lines) is deterministic to detect. A model review
of code that a ratchet would fail wastes the expensive resource on the cheap defect.

## Decision

Four mechanical, model-free layers run around every change in the agent's own loop
(orientation map pre-write, YAGNI ladder during write, quality ratchets and architecture diff
post-write via Stop hooks), and the cross-vendor review runs only on what survived them.
Adoption order from nothing: ratchets, architecture diff, then the two pre-write layers.

## Consequences

- Positive: the review's surface shrinks to intent, security, design and novel risk; the
  mechanical layers produce inspectable output for dashboards; zero hallucination risk in the
  first four layers.
- Cost: per-machine binaries, a tracked settings file that is a supply-chain tripwire, and a
  guard that occasionally refuses legitimate commands. Third-party plugins need vetting and real
  pins before use on company machines.
- Follow-ups: trial the two pre-write layers on a complex multi-file task before rollout;
  confirm the orientation index in a worktree-per-agent layout.

## Alternatives rejected

- Review everything with the model: measured cost, and the model does not see what a
  baseline sees (a regression among hundreds of existing findings).
- Linters only: no baseline, so no way to separate introduced from inherited debt; no cycles
  across files; no layer order.

## Evidence

- `docs/05-sensor-stack.md`; `STATUS.md`, the quality-ratchet, architecture-diff and cross-vendor
  review rows.
