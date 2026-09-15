<!--
  PROGRAM DESIGN NOTE (BUILD stage, before the plan). Written by the head, the person or
  the top-tier session holding the dev hat, after the ticket is Ready and before any brief
  is written. It fills the gap between the architecture (which modules exist and how they
  talk) and the code: the types, signatures, call paths and file layout this change adds or
  alters, and the order the slices land in. It exists so that review checks agreed decisions
  instead of discovering them in a finished diff.
  One note per sized ticket. A one-shot ticket (the sizing rule in docs/02-loop) skips it and
  the plan says so. Sections stay; write "none" rather than deleting a heading.
-->

# Program design: <ticket key and title>

- Ticket: `<id>`, approved version <vN>
- Size: <one-note | full>, by the rule in [02-loop](../docs/02-loop.md); the reason in one line
- Author: <role>. Reviewed by: <one cross-vendor leg | the panel and the owner, for a full ticket>
- Architecture inputs: <decision records, module map, contract file, design handoff this note builds on>

## 1. Modules and lanes

<!-- The modules this change may touch, from the repository's module map or the architecture
     diff tool's layer declaration. This list is the scope the spillover check runs with; a
     file outside it is a gate failure, not a judgement call. Lanes for parallel stations are
     disjoint by construction here, never negotiated after the fact. -->

| Module | Layer | Lane (station) | Change kind (new, extend, retire) |
|---|---|---|---|
| | | | |

## 2. Types and data

<!-- Every type, schema, table column, enum and message this change adds or alters, with its
     owner module. Prefer making bad state unconstructable to checking for it. A name here is
     the name the tests, the contract and the UI will use; a brief cites this table, never a
     consumer's type (cycle 4 planted a wrong field name from a frontend type and both review
     legs had to catch it). -->

| Type or column | Module | New or changed | Invariant |
|---|---|---|---|
| | | | |

Migration: <none | forward-only | reversible | data backfill>; row-level policy touched: <none | which>

## 3. Signatures and call paths

<!-- The functions, methods, endpoints and jobs added or changed, with their signatures as
     they will read in code, and the call path from the entry point down. Anything the
     orientation map (sensor 1) says already exists and does this is reused here by name,
     never rewritten. -->

- `<entry: route or job>` calls `<service.method(args) -> Result>` calls `<repository.call>` on `<table>`
- Reused as is: `<symbol>` (found with the orientation map; callers today: <n>)
- Retired: `<symbol>`; its last caller is removed in slice <n>

## 4. Shape decisions

<!-- The choices a builder would otherwise make alone on its way past: streaming or buffered,
     batch size, idempotency key, error format, transaction boundary, retry policy, locale
     handling, pagination. One line each, with the rejected option. The head-and-hands trial
     spent one of four rounds on a shape choice (per-fragment sends) the brief had left open. -->

| Decision | Chosen | Rejected | Why |
|---|---|---|---|
| | | | |

## 5. Slices, in landing order

<!-- Vertical slices: each crosses every layer it needs and is verifiable on its own. The order
     is the order the plan and the briefs follow. Each slice names the numbered examples it
     satisfies and the check that proves it, so a station can stop at a slice boundary and
     leave the branch coherent. A horizontal plan (all models, then all services, then all UI)
     is what a model produces unsteered, and is refused here. -->

| # | Slice | Examples (AC-n) | Check | Station |
|---|---|---|---|---|
| 1 | | | | |

## 6. Tests that must be red on the merge base

<!-- The behaviours the new tests will assert, named before the tests exist. The fail-on-base
     check (docs/05-sensor-stack) later confirms each listed test fails on the merge base and
     passes on the branch. A test that would pass on the base is either declared here as a
     characterization or refactor test with its reason, or it is not a test of this change. -->

- `<test module::test name>` proves AC-<n>; red on base because <what does not exist yet>
- Declared exemptions: <none | `<test id>`: characterization of existing behaviour | `<test id>`: moved by the refactor>

## 7. What the reviewer checks against this note

<!-- Read by the panel as one more injected pack (docs/06-verify-gate, spec conformance). Drift
     from sections 1 to 5 is a spec-drift finding citing the section; intended drift takes the
     disposition REFINE-SPEC and is written back here before merge, so the note stays the
     record of what was built. -->

- Files touched are inside section 1 (mechanical: the spillover check).
- Names in code match sections 2 and 3.
- Every row of section 4 is implemented as chosen, or the drift is a finding.
- Slices landed in the order of section 5, or the PR says why not.
- Every test in section 6 was red on the merge base (mechanical: the fail-on-base check).
