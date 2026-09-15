# Architecture Decision Records

Why this repo is the way it is. Each ADR captures **one** decision, its context, and its
consequences. ADRs are the audit trail a due-diligence reviewer reads — keep them honest.

## Format

MADR-lite. Copy `0000-template.md` to `NNNN-<kebab-title>.md`:

- `NNNN` — zero-padded, monotonically increasing (next number after the highest existing).
- One decision per file.
- **Status**: `proposed` → `accepted` → (`superseded-by-NNNN` | `deprecated`).

## Rules

- **Never edit an accepted decision.** Superseding a decision means: write a new ADR,
  set the old one's status to `superseded-by-NNNN`, and reference it from the new one.
- Record a decision when it is architecturally load-bearing (affects structure, a
  contract, data, security, or something expensive to reverse). Don't ADR trivia.
- Link the ADR from `../architecture.md` and, where relevant, anchor a memspec `decision`
  to it.

## Index

| # | Title | Status |
|---|---|---|
| [0001](0001-adopt-context-standard.md) | Adopt the context standard | accepted |
