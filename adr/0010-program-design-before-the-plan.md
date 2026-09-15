# 0010. Program design before the plan; red-first becomes a gate

- **Status:** proposed
- **Date:** 2026-09-15
- **Deciders:** the operator, the principal session that proposed it

## Context

Two gaps this design has carried since its first version. Both were named on 2026-07-26, when
the operator mapped the group's built estate against a public argument about why software
factories fail ([evidence/field-evidence.md](../evidence/field-evidence.md) §7), and neither had
been closed by 0.2.9.

The argument, in one paragraph. Coding models are trained by reinforcement on a reward of the
shape "the hidden tests pass and nothing regressed". Nothing in that reward prices architecture,
whose cost arrives months later, so a model gets better at passing tests and no better at
keeping a codebase changeable. Two consequences for this design: the review gate does not
sunset with model releases (the justification for [adr/0003](0003-cross-vendor-non-inheriting-review-is-the-merge-gate.md)
and [adr/0006](0006-pr-gated-output-human-release.md) that outlasts any one model), and the
cheapest place to decide the shape of a change is before the diff exists.

**Gap 1: nothing between the ticket and the code.** The ticket says what changes in observable
terms ([templates/ticket.md](../templates/ticket.md)); the knowledge plane says which modules
exist and which decisions stand. Neither says which function gains which parameter, where the
transaction boundary sits, whether an export streams or buffers, or which slice lands first.
Measured costs of leaving that to the builder:

- The head-and-hands trial spent one of four hands rounds on a redesign after the cross-vendor
  reviewer found the shape wrong (per-fragment sends, 32,018 for 2,000 rows). Tests and lint
  were green because the output was byte-identical `[measured 2026-09-05]`.
- Cycle 2's planning document carried pseudocode keyed on a retired flag that production still
  held as `true`; a literal implementation would have auto-activated payments without fresh
  consent. Found by the reviewer in the diff stage, classified MEDIUM `[measured 2026-09-07]`.
- Cycle 4's brief stated a field name taken from a frontend type that was itself wrong; both
  review legs flagged a field that did not exist on the API `[measured 2026-09-09]`.

Cycle 4 also holds the measured precursor of the fix: one scout produced a code map, the
principal wrote an API contract (storage columns, two endpoints, CSV shape, recording rules),
and three stations built to it in parallel on disjoint worktrees `[measured 2026-09-09]`. The
contract was a program design note in all but name, reviewed only after the build.

**Gap 2: "red first" is a rule and a hand step.** [02-loop](../docs/02-loop.md) has said "tests
first, red on the unfixed code" since cycle 1, and the gate report has a `red-before` row. Both
are done by hand: a fix reverted, a test rerun, a line written `[measured 2026-09-07]`.
Principle 1 says every rule is written twice, as the rule and as its check, or labelled
advisory. This one was never labelled. The local measurement of what the missing check costs
is the trial's MINOR: a behavioural test that only proved a function was unused, where a
`list(...)` would have passed `[measured 2026-09-05]`. A public evaluation cited in the same
talk (FrontierCode) applies exactly this check to agent-written tests: a test that does not
fail against the pre-patch code has not shown it detects the behaviour the patch repairs.

## Decision

We will make program design a named first step of BUILD for sized tickets, and make red-first
a gate.

1. **Program design note.** For a ticket above one-shot size (the sizing rule in
   [02-loop](../docs/02-loop.md): two or more modules, or a new type, column or migration, or
   parallel stations, or a money, tenant or identity path), the head writes
   [templates/program-design.md](../templates/program-design.md) before the first brief:
   modules and lanes, types, signatures and call paths, shape decisions with the rejected
   option, slices in landing order, and the tests that must be red on the merge base. One
   cross-vendor leg reviews the note before any brief (the panel and the owner for a full
   ticket); the reviewer flags and never edits. The note travels to the review panel as one more
   injected pack, so drift from it is a `spec-drift` finding citing the section and intended
   drift takes REFINE-SPEC ([adr/0009](0009-the-spec-is-a-gate-input.md)). Its module list is
   the scope the architecture diff's spillover check runs with. The hands never design.
2. **Fail-on-base check.** Every test the diff adds or changes is run at the merge base with the
   branch's test files applied and must fail there; the same tests must pass on the branch. The
   failure kind is recorded (an assertion is the strong witness; a collection or import error is
   weak, and a weak witness on a money, tenant or identity path is a finding). Only declared
   exemptions may pass on the base: characterization tests, tests moved by a refactor, tests for
   a defect fixed earlier on the same branch, each named with its reason in the note or the plan.
   Deleted tests are reported on their own line every time. The check runs on the Stop hook when
   the selected tests need no database or browser, otherwise as a receipt-checked pre-push gate
   in the shape the browser and static-analysis passes already use.

Scope: 1 applies to sized tickets only; a one-shot ticket records its size in the plan and
needs nothing else. 2 applies to every diff that touches a test file.

## Consequences

- **Positive:** review checks agreed decisions instead of discovering them; shape decisions
  get a rejected alternative on record before they are code; the red-first rule cannot be
  skipped silently; the reviewer stops being the party that discovers a test proves nothing;
  parallel lanes are disjoint by construction rather than by negotiation.
- **Cost:** one note per sized ticket (a page; the cycle-4 contract was written inside the
  2 h 08 min to the backend PR and is not separately timed), plus one review leg on it, minutes
  for a page; two runs of the selected tests plus a temporary worktree per gate run; the sizing
  rule needs calibration on the first sized tickets and will be wrong somewhere at first.
- **Follow-ups:** the check script on the reference implementation, one per stack, with its
  receipt (owner: the operator, a ticket in the reference ledger); note injection to the review
  tool, sharing the [adr/0009](0009-the-spec-is-a-gate-input.md) pack plumbing (owner: the
  tool's maintainer); the rework-share metric in the cycle report
  ([10-measurement](../docs/10-measurement.md)) so the note's payoff is a number; both checks
  rehearsed in the blocked direction before either is trusted (a planted test that passes on
  the base is refused; a file outside section 1 fails the spillover check); the sizing rule
  re-cut after five sized tickets.

## Alternatives considered

- **Put the design in the ticket:** the PM hat does not write signatures, and a ticket that
  carries them stops being the delta. Rejected; the note is a dev-hat artifact that cites the
  ticket's examples by number.
- **Leave it to plan mode:** the measured plans are step lists with a model tier per step. A plan
  produced without a design is horizontal by default (all models, then all services, then all
  UI), and the slice order is exactly what a model does not produce unsteered. Rejected.
- **The authoring session reviews its own note:** the same solo judgement the gate exists not
  to trust ([adr/0003](0003-cross-vendor-non-inheriting-review-is-the-merge-gate.md)). Rejected;
  one cross-vendor leg on a page is minutes.
- **A design note for every ticket:** cycle 1 (+47/−1, one module) needed nothing, and
  mandatory design on one-line fixes reproduces the review-load failure one stage earlier.
  Rejected in favour of the sizing rule.
- **Mutation as the only test-strength check:** mutation asks whether the existing suite notices
  a planted change in the code; fail-on-base asks whether the new tests notice the change they
  shipped with. Different questions, both kept.
- **Accept any failure on the base:** the weaker check; an import error proves the test needs
  the change, not that it detects it. Rejected; the kind is recorded and gates on the money lane.
- **A CI job instead of the Stop hook or a receipt:** it runs after the push, so the PR arrives
  unproven, the same reason the browser pass moved before the push ([adr/0008](0008-browser-qa-drives-a-cli-not-a-protocol-server.md)).
  Rejected as the gate; fine as a follow-up.

## Evidence

- [case-studies/kvart-head-hands-trial.md](../case-studies/kvart-head-hands-trial.md): the
  rounds table (round 3 redesign), the SERIOUS and the MINOR.
- [docs/06-verify-gate.md](../docs/06-verify-gate.md), "What the gate caught": cycle 2's
  planning-document MEDIUM.
- [case-studies/kvart-reference-implementation.md](../case-studies/kvart-reference-implementation.md),
  cycle 4: contract-first stations; the planted field name.
- [docs/05-sensor-stack.md](../docs/05-sensor-stack.md), layer 3: the mutation subsection this
  check sits next to, and the fail-on-base design.
- [evidence/field-evidence.md](../evidence/field-evidence.md) §7: the public argument and the
  public evaluation's check.
