# 0016. The reviewer gets a computed impact set, and every module in it gets a verdict

- **Status:** proposed
- **Date:** 2026-10-15
- **Deciders:** the operator, the principal session that proposed it

## Context

A senior engineer on one of the group's teams briefs every adversarial reviewer with the modules
a change affects, not only the diff: "if this changes, look at that". The practice is tacit and
unmeasured. It names a question this design answers only in part: who decides which code outside
the diff the reviewer reads, and how anyone checks that it was read.

Three mechanisms touch it today, and none of them hands the reviewer a set:

- **Builder side.** The orientation map answers `--impact` and `--callers` before a write
  ([05-sensor-stack](../docs/05-sensor-stack.md) layer 1). It is a pre-write aid, not a gate, and
  a headless builder with it available made 0 calls to it `[measured 2026-09-29]`.
- **Plan side.** Section 1 of the program design note is the scope of the spillover check
  ([adr/0010](0010-program-design-before-the-plan.md), layer 4). It bounds what the builder may
  touch. It says nothing about what the change affects.
- **Review side.** The review tool always injects its blast-surface pack, whose step 2 orders a
  consumer sweep over the whole repository. Each leg re-derives the affected set by its own
  search. The diff-only transport cannot sweep at all
  ([06-verify-gate](../docs/06-verify-gate.md)), and a repo-reading leg can skip it: in one trial
  run the second-vendor leg made 0 tool calls, so it reviewed the diff without reading the
  repository ([evidence](../evidence/kvart-sensor-trial-2026-09-29.md)). No report says which
  consumers a leg looked at, so a clean verdict cannot be told from an unswept one.

A static call graph alone does not close this. The escapes measured so far cross edges that
static analysis does not model:

- **A whole-tree fence.** A PR added 2 error codes without translations. Impact selection ran 78
  targets and never picked the translation fence, because the selector maps a file to the tests
  that import it and a fence that scans the tree imports nothing specific
  ([evidence](../evidence/kvart-stale-green-merges-2026-09-29.md), case B,
  `[measured 2026-09-29]`).
- **A registration.** Cycle 2's payment status poller had no caller in the web client; it ran
  because a job registry and a timer unit scheduled it, and it was the only hop that closed a
  payment state (adr/0012, `wired_by`; [evidence](../evidence/kvart-dogfood-cycle-2.md),
  `[measured 2026-09-07]`).
- **Framework dispatch.** On a service of the group's estate built on command dispatch, a code
  graph tool that resolved dependency injection returned 0 callers for a command whose handler a
  text search found in 2 s. The handler held a confirmed object-level authorization defect
  `[measured 2026-07-21]`. The estate dispatches commands and events this way throughout.

The cost side is known. Less context is more accurate (layer 1, LongCodeBench), so pointing every
leg at the whole repository is not an answer, and the review is already the largest block of
wall-clock per turn ([06-verify-gate](../docs/06-verify-gate.md), Cost).

Assumptions, stated: the orientation map or the architecture diff tool can list the dependents of
a changed symbol at module granularity; the review tool's schema can carry one more field; a
person can name a team's dispatch edges in an afternoon, as the senior already does from memory.

## Decision

We will compute the affected modules of every code diff by script, hand them to every review leg
as an input pack, and refuse the gate when a module in the set has no evidenced verdict.

1. **The seams file.** A `seams.yaml` in the code repository lists the edges a static graph
   misses. One entry per seam: an id, a trigger (path globs, symbol or annotation patterns), the
   modules or checks it reaches, and the reason in one line. Seam kinds: command or event to its
   handlers; scheduled jobs and their registrations (shared with the money path map's `wired_by`,
   adr/0012, never duplicated); tables written by one module and read by another; whole-tree
   fences (translations, error codes, permissions catalogues); contracts another repository reads.
   It is seeded by the people who hold the "if X changes, look at Y" knowledge, and a resolver
   checks that every trigger still matches something in the tree, in the shape of adr/0012's.
2. **The impact set.** A script reads the diff, takes the changed symbols, and writes
   `impact-set.json`: the modules reached by static dependents (the orientation map's
   `--impact`, or the architecture tool's impact analysis), the modules and fences reached by any
   seam whose trigger the diff matches, and the touched money path entries. Each module carries
   its reason (an edge or a seam id). Changed symbols, not changed files, so a one-line edit in a
   hub module does not pull in every importer of that module. The set is capped at 12 modules (a
   starting value for the measurement below), ranked seams first, then by edge distance. A set
   over the cap is reported as truncated, and a truncated set on a one-shot ticket
   reclassifies it as one-note under adr/0010's sizing rule.
3. **The pack.** The set travels to every leg as one more injected pack, the mechanism adr/0009
   uses for the spec. The instruction: for each listed module, state `checked-clean`,
   `finding`, or `not-inspected`, and cite at least one `file:line` read in that module. A
   verdict without a citation counts as `not-inspected`. The diff-only transport receives the
   set too and answers `not-inspected`, which is honest; it is not asked to pretend.
4. **The coverage check.** The review schema gains a `coverage` array (module, verdict,
   citations). A script over the merged panel output refuses the gate when a module in the set
   has no `checked-clean` or `finding` verdict from at least one repo-reading leg, and names the
   module. A citation that does not resolve to an existing line in the tree counts as no verdict.
   The adjudicator spot-checks one `checked-clean` verdict per panel against the cited lines, as
   it already disbelieves one rejected finding.
5. **Escapes grow the file.** A finding the adjudicator confirms in a module outside the set, and
   any post-merge regression traced to a module outside it, adds a seam in the same PR as the fix.
   A seam is removed only by a person, with a reason, like a baseline (adr/0004).
6. **One file for review and test selection.** The CI test selector reads the same seams, so a
   whole-tree fence triggered by a diff is selected as a target. This closes case B at both ends:
   the reviewer is told about the translation fence and CI runs it. The repo-wide fences on every
   PR from 06 stay; this makes the selection explicit rather than relying on a list kept elsewhere.

Scope: every code diff that reaches the cross-vendor panel. Docs-only diffs are exempt as today.
The blast-surface sweep stays: the set is a floor for what must be read, never a ceiling, and a
leg still reports consumers it finds outside it.

## Consequences

- **Positive:** the senior's briefing becomes a file every reviewer gets, and survives the
  senior; "the reviewer looked at the handler" is checkable from the report instead of assumed; a
  leg that read nothing fails the coverage check instead of returning a clean result; the three
  measured escape shapes (whole-tree fence, registration, dispatch) each have a seam kind that
  would have listed them.
- **Cost:** a seeding session per repository with the people who hold the knowledge; upkeep on
  every escape; longer reviews, by an amount to measure (each listed module is at least one read
  per repo-reading leg); one more field in the review schema and a check script; the cap will
  sometimes truncate a real dependent, which the sweep and the truncation line in the report have
  to cover.
- **Follow-ups:** the review tool: impact pack injection, the `coverage` field in the findings
  schema, the coverage check over the merged panel output (owner: the tool's maintainer); the
  reference implementation: kvart's `seams.yaml` seeded with the translation and error-code
  fences, the job registry and timer units, and the shared tables, plus the resolver with planted
  true and false cases (owner: the operator); rehearse the blocked direction: replay case B and
  cycle 2's poller removal against the set and show each module listed and each unswept verdict
  refused (owner: the operator); measure on the next 5 sized tickets: modules listed, verdicts
  evidenced, findings inside versus outside the set, review wall-clock against the cycles before
  (owner: the operator); on the group's estate, a seam extractor for command and event handler
  annotations, so the dispatch edges are generated rather than typed (owner: the group's platform
  role).

## Alternatives considered

- **The status quo, the blast-surface sweep alone:** kept, as the open-ended part. Rejected as
  the only mechanism: each leg re-derives the set, the diff-only transport cannot, a leg can skip
  it, and nothing records what was covered.
- **A static call graph alone:** blind to command dispatch (0 callers where a text search found
  the handler), to registrations, and to whole-tree fences. Kept as one input of the set.
- **A hand-kept list alone, in the shape of CODEOWNERS:** catches the tacit edges and misses
  ordinary callers, and rots without a resolver. Kept as the seams file, with the static graph
  beside it and the resolver behind it.
- **Point every leg at the whole repository:** more context lowers accuracy, and it says nothing
  about coverage. Rejected.
- **A caller-reading review skill on the authoring vendor** (Ponytail 5's `/ponytail-review`
  reads callers of every changed function `[field: Ponytail 5]`): an
  LLM-derived set, same vendor, no coverage check. At most a cheap pre-PR self-review; it does
  not satisfy this decision or the vendor axis.
- **One reviewer per affected module:** a fan-out that costs one review per module. Deferred
  until a set routinely exceeds the cap; the coverage check is the cheaper first step.

## Evidence

- [evidence/kvart-stale-green-merges-2026-09-29.md](../evidence/kvart-stale-green-merges-2026-09-29.md):
  case B, the fence impact selection never picked `[measured 2026-09-29]`.
- [evidence/kvart-dogfood-cycle-2.md](../evidence/kvart-dogfood-cycle-2.md): the poller with no
  web caller `[measured 2026-09-07]`.
- [evidence/kvart-sensor-trial-2026-09-29.md](../evidence/kvart-sensor-trial-2026-09-29.md): the
  headless builder's 0 orientation-map calls; the review leg with 0 tool calls.
- The command-dispatch A/B on a group service `[measured 2026-07-21]`: the operator's notes, not
  yet copied into `evidence/`.
