<!--
  TICKET (SPEC stage). Written by the person holding the product hat, before any agent
  is allowed to touch code. It is the one approved request the whole cycle is graded
  against: the builder expands it, the verifier checks against it, and acceptance is a
  decision on these examples, not on the diff.
  Copy this file per ticket. Delete nothing: a section with no content is itself a
  finding, so write "none" rather than removing the heading.
-->

# <short title, 3 to 8 words, no trailing punctuation>

**Stage:** Backlog → Ready → In Progress → In Test → Ready for LIVE → LIVE
<!-- Mark the current stage in bold. The stage line is the only status field; no
     parallel status lives in a comment thread or a chat message. -->

**Readiness:** <n>/100, self-scored against the rubric in `<path to your readiness rubric>`
<!-- The author scores the ticket before handing it over. A ticket below the team's
     threshold (start at 85) goes back for another pass rather than into BUILD. The score
     is a claim about this document, not about the feature. -->

## User problem

<Who hits this, when, and what goes wrong today. Two to four sentences. State why now.
A link alone is not a problem statement.>

## Desired result

<One paragraph. What is true for that person once this ships, in observable terms. No
implementation instructions.>

## Exclusions

- Out of scope: <thing a reader would reasonably assume is included, and is not>
- Out of scope: <second one, if any>

## Prototype views (UI work only; otherwise "none")

<!-- One line per screen this ticket changes or introduces: `<prototype file>#<view id>`.
     A route this ticket's screens open must have a named view here or in another Ready
     ticket, or it is a missing story. The verifier compares the build's screenshot with
     the named view; "opens the X list" without a view is satisfiable by the old screen. -->

- <screen name>: `<prototype file>#<view id>`

## Examples

<!-- Numbered examples are the contract. Each one names a starting state, an action, and
     an outcome an independent party can observe without reading the code. AC-n numbering
     is enough; no schema and no separate requirements store. The same numbers are quoted
     by the build plan, the test names and the evidence, so a PASS can be traced to the
     example it satisfies. -->

**AC-1**
- Starting state: <the data and permissions that exist before the action>
- Action: <what the actor does, in one sentence>
- Expected observable outcome: <what is visible afterwards, with the exact value where a
  value is involved, and where it is visible>

**AC-2**
- Starting state: <...>
- Action: <...>
- Expected observable outcome: <...>

**AC-3 (failure path)**
- Starting state: <...>
- Action: <the unauthorised, duplicate, expired or malformed case>
- Expected observable outcome: <the refusal, the error shown, and what must not have
  changed>

## Constraints and failure cases

- Invariant that must not break: <name it, and name the check that proves it>
- Surface allowlist: <paths, services or APIs this change may touch; everything else is denied>
- Performance or capacity budget: <number with units, or "none">
- Unresolved rule: <the business question this ticket does not answer>, owner: <role>
<!-- Every unresolved rule carries a named owner role. An unresolved rule with no owner
     blocks the ticket from reaching Ready; it does not become a decision an agent makes
     on its way past. -->

## Escalation triggers

<!-- Conditions that stop execution and surface to a human immediately. Without this list the
     agent infers its own bail-out criteria, which is how scope creep and silent substitution
     happen. Write at least one. -->

- Escalate when: <condition that requires a human decision, e.g. a schema change appears necessary>
- Escalate when: <tests fail three times for the same reason without a clear fix>
- Escalate when: <the desired result conflicts with an existing product rule or invariant>

## Approval

- Approved version: <vN>, <YYYY-MM-DD>
- Approver: <role>
<!-- Approval attaches to this version of the text. A material change to the problem, the
     desired result or any example returns the ticket to Ready and needs a new version and
     a new approval. Regenerating a spec from shipped code must never be treated as
     approval of that code. -->

## Design artifacts

<!-- UI tickets only; delete the section otherwise. The agreed prototype is attached to
     the ticket in the ledger (throwaway banner and fake data intact), never copied into
     the team layer. It is a load-bearing input for the builder: arrangement, states,
     copy. It is not an implementation instruction. Decided 2026-09-09, not yet measured. -->

- Prototype: <attachment name on the ticket>
- Patterns expected: <numbered patterns from the design standards>
- Components expected: <components from the design standards; anything not listed is invention and the reviewer treats it as such>

## Links

- Build branch or PR: <fill in during In Progress>
- Sister spec change: <fill in during In Progress>
- Evidence: <path to the gate report>
