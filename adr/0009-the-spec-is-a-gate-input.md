# 0009. The spec is a gate input; scope drift is a finding with its own disposition

- **Status:** proposed
- **Date:** 2026-09-10
- **Deciders:** the operator, the principal session that proposed it

## Context

ADR 0007 makes specs the implemented state and keeps them current by a sister PR on every
behaviour-changing code PR, at LEARN, after merge. Two consequences were measured on kvart.

The reviewer never sees the spec. The cross-vendor review reads the diff plus injected rule
packs; the spec lives in a different repository. In cycle 4 the repo-reading leg raised the
management-company scope question from the code alone, the principal dismissed it "by the spec"
and escalated it as D1. The three panels ran 11:16 to 12:36Z; the escalation thread with D1 to
D5 was posted at 12:53Z, so no reviewer had the decisions either `[measured 2026-09-09]`. The
one party holding the spec was the authoring session, whose solo judgement the gate exists to
not trust (ADR 0003).

The delta lags. Cycle 4's pre-build spec (team-context PR 8) was unmerged at build time and
is still open. Its sister delta (PR 10) branches off it, is still open, and records by hand
five refinements the shipped code made to the text. Cycle 5's delta is the first open item in
its handoff `[measured 2026-09-10]`. Cycle 1's delta was typed by hand because the generating
skill was absent `[measured 2026-09-07]`. In three of five cycles the LEARN edge for specs was
late or manual.

The obvious fix, asking the reviewer to compare the diff with the ticket, was considered and
is weaker. A ticket is two paragraphs of desired state; a reviewer asked to check conformance
against it fills the gaps with invented spec text. A committed spec plus the ticket's numbered
examples is the anchor that makes the comparison mechanical enough to trust.

## Decision

We will make the spec a VERIFY input, not only a LEARN output.

1. The review panel receives the feature's current spec, the ticket's numbered examples and the
   escalation-thread decisions taken so far, injected as one more pack so every leg sees them,
   including a leg that reads only the diff payload. Findings gain a class, scope drift, in
   both directions: behaviour in the diff the spec does not describe, and spec behaviour the
   diff claims and does not deliver. Each cites the spec section.
2. Dispositions gain REFINE-SPEC: the drift is intended, so it is written into the sister spec
   delta (and into the escalation thread when it is a product call), and the finding closes
   when the delta records it. Cycle 4's five hand-written refinements become gate output.
3. The sister spec delta PR is opened at gate time (a stub is enough) and becomes a
   receipt-checked pre-push gate in the same shape as the browser pass: a behaviour-changing
   diff without a delta receipt for its tree does not push. The pre-build spec is merged, or
   its commit is pinned in the station brief, before pickup.

Scope: behaviour-changing diffs. A pure refactor carries a delta that says "none", as today.

## Consequences

- **Positive:** the reviewer's scope questions cite a section instead of guessing; refinements
  reach the spec during the cycle instead of from memory afterwards; the delta cannot lag the
  merge, by construction rather than by discipline.
- **Cost:** one more pack in the reviewer prompt (a spec with its tech-refs is well under the
  64 KB cap); a stub PR per cycle; the panel needs the spec path, which the station brief
  already names. Cross-repo: the station's tree needs the team-context checkout, or a fetched
  copy at the pinned commit.
- **Follow-ups:** the review tool: spec pack injection and the scope-drift instruction (owner:
  the tool's maintainer; kvart KVART-24); the reference implementation: delta receipt in the
  pre-push hook and REFINE-SPEC in the report templates (owner: the operator; kvart KVART-23); measurement: the class is tested
  against a planted drift and a known-conformant diff before it is trusted, and demoted to
  advisory if more than half of its findings on the first live cycle are dismissed.

## Alternatives considered

- **Compare the diff with the ticket text:** two paragraphs of desired state; the reviewer
  invents the rest. Rejected as the noisier signal.
- **Let the repo-reading legs read the specs themselves:** the specs are in another
  repository, and one leg reads only the diff payload. Rejected; injection reaches every leg.
- **Leave conformance to the principal at adjudication:** what cycle 4 did. The principal is
  the authoring session; ADR 0003 exists because that judgement alone is not the gate.
- **Fold every decision into the spec before the gate runs:** decisions emerge during BUILD
  and VERIFY; cycle 4's were posted after all three panels had finished. Requiring them first
  blocks the gate on a thread. Rejected in favour of the disposition, which lets the gate
  produce them.

## Evidence

- The cycle 4 dogfood report and its timeline: panels 11:16 to 12:36Z, ESCALATE 12:53:24Z,
  defaults standing 13:49:02Z; the "dismissed by the spec" adjudication of the scope finding.
- team-context PR 8 (pre-build spec, open at build time) and PR 10 (sister delta, open,
  "five refinements the shipped code made to the text"); the cycle 5 handoff, open item 1.
- The review tool's reviewer instruction and its rule-pack injection block, which carry no
  spec input today.
