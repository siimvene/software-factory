---
name: mine-decision-records
description: Mine a codebase's design documents and rule files for architecturally load-bearing decisions that are live in the code, confirm each against code, and write the confirmed ones as numbered decision records (repo-level in the code repo, team-level in the team-context repo). Use whenever the user asks to bootstrap ADRs, mine decision records, find the architecture decisions in a repo, or turn design docs into ADRs. Triggered by phrases like "mine the ADRs", "what decisions are live in this code", "bootstrap decision records", "write the ADRs for this repo".
allowed-tools: Read, Grep, Glob, Write, Bash
---

<!-- Written for the reference design on 2026-09-10 from the procedure the reference
implementation ran on Day 1 (docs/17-onboarding.md, section 6). The procedure was run by
hand there; this file makes it repeatable. Rename freely, keep the firing conditions. -->

# Mine decision records

Turn the decisions a codebase already embodies into records an agent will read before it
changes anything. The one failure this skill exists to prevent: a decision that lives only in
a design document, or only in someone's head, gets reversed by an agent that never saw it.

A record is written only for a decision that is **live in the code**. Design documents
describe intent; the code is the evidence. A candidate whose code evidence cannot be found
stays a candidate.

## Inputs, in read order

1. The decision-record template: `templates/adr.md` in the reference repository, or the
   team's own if it has one. Its sections are the shape of the output.
2. Existing records in `docs/adr/` of the code repo and of the team-context repo, so numbering
   continues and nothing is re-decided.
3. Design documents: `docs/`, architecture notes, README sections that explain a choice.
4. Agent rule files (`.claude/rules/`, the root instructions file): a rule that constrains
   how code is written is often an unrecorded decision.
5. The code, for evidence only. Never write a record from a document alone.

## Procedure

1. **Sweep.** Read inputs 3 and 4 end to end. Note every sentence that constrains structure,
   contracts, data, security, deployment, or a boundary between systems. Ignore feature-level
   UX choices, visual design, commercial terms and anything that would change with the next
   sprint; those go to the rejected list (step 5), with the reason, so nobody re-raises them.
2. **Candidate table.** One row per candidate in `docs/adr/CANDIDATES.md` of the code repo:

   | Proposed title | Decision, one sentence | Source documents | Code evidence paths | Status | Note |

   Status is one of `candidate`, `unconfirmed`, `written NNNN`, `rejected`. Sort by the area
   of the codebase the decision governs. Do not truncate; a long table is the point.
3. **Confirm against code.** For every row, find the code that proves the decision is live:
   a module boundary, a database policy, an adapter interface, a deploy unit, a migration
   pattern. Record the paths in the evidence column. A row with no evidence becomes
   `unconfirmed` with a note saying what would confirm it (often: "check on the production
   box which mode is active"). Do not write a record for an `unconfirmed` row.
4. **Split by level.** Repo-level records (structure, contracts, data, security, deployment
   of this repo) go to the code repo's `docs/adr/`. Team-level rules that hold across every
   repo of the product (money is decimal end to end, API enum values in one language, the
   mobile client consumes the public API only, agents never move money) go to the
   team-context repo's `docs/adr/`. Say in the note which level each row is.
5. **Rejected list.** At the end of `CANDIDATES.md`, a section "Rejected as not record-worthy"
   with each item and its reason in one line.
6. **Write the records.** For every confirmed row, one file from the template, numbered
   sequentially after the last existing record in that repo, filename
   `NNNN-<kebab-title>.md`. Every section filled: the context names the forces, the decision
   is one or two sentences in the active voice, the consequences name a cost, the
   alternatives name at least one option that was weighed and dropped, the evidence lists
   the code paths from the table. Update the table row's status to `written NNNN`.
7. **Front doors.** Add each new record to the `docs/adr/README.md` index of its repo, in the
   format that file already uses.
8. **Handoff.** The records enter through a pull request the owner reads. Prepare the branch,
   the PR title and a body that lists every record with its one-sentence decision and the
   count of candidates left in the table. The human submits or merges.

## Output

- `docs/adr/CANDIDATES.md` in the code repo (the table, the rejected list).
- `docs/adr/NNNN-*.md` files in the code repo and in the team-context repo.
- Updated `docs/adr/README.md` in each.
- One PR per repo, opened by the agent or handed to the human as a package.

Reference numbers, so a run can be judged: the reference implementation's Day 1 produced a
table of 30 candidates, 13 repo-level records, 8 team-level records, and left the rest in the
table with the rule that each becomes a record when its code is next touched. One candidate
stayed `unconfirmed` because the active storage mode could not be read from the repository.

## Self-check before handing off

- Every record's evidence paths resolve in the checked-out tree (`ls` each one).
- No record was written from a document without code evidence.
- Numbers continue the existing sequence; nothing was renumbered or deleted.
- Every record has at least one rejected alternative.
- No person is named in any record; roles only.
- The candidates file has a rejected list with reasons.

## Refuse to

- Write a record for a decision that is not live in the code, however well documented.
- Renumber, rewrite or delete an existing record. A decision that turned out wrong gets a new
  record that supersedes it.
- Merge or push. The records are a proposal until a person has read them.
- Name people. Deciders are roles.
- Record feature-level UX, visual design or commercial terms as architecture.
