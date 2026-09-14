# Knowledge plane

Everything an agent reads that is not the code, where each piece lives, who may write it, and
how it stays true. The design follows a repository context standard with four layers; this
document says what the layers are for in a software factory and what the kvart adoption measured.

## The four layers

| Layer | Lives in | Written by | Reaches the agent via |
|---|---|---|---|
| Operating contract | one managed file, vendored into every repo | the organisation, by reviewed PR | auto-loaded at session start |
| Repo layer | the code repo: agent instructions, path-scoped rule files, decision records, current-state docs | the code owner, in the same PR as the code | auto-loaded; rule files load when a matching path is read |
| Team layer | the team-context repo: specs, cross-repo decision records, memory store, review rubric | agents by promote PR; humans merge | read-only binding from each code repo |
| Working memory | local scratch store on the operator's machine | the agent, at the moment of discovery | search at session start; disposable |

Conformance is graded (L0: instructions, memory binding, decision records, current-state docs
present; L1: a decision record for every live architectural decision; L2: a docs-lint gate),
and a repo adopts gradually. kvart adopted at L0 on 2026-09-07 and bootstrapped L1's decision
records the same day.

## Repo layer: instructions that stay lean

The agent instructions file used to be one 25 KB block loaded into every session. It was split
into a root that carries only what applies to every change (what the product is, the stack,
conventions, parallel-agent rules, commands) plus path-scoped rule files that load when a file
matching their globs is read. A session starts lean and the subsystem rules arrive when the
code they govern is touched `[measured 2026-09-01]`.

Two rules about the rule files:

- Content moves verbatim; a new invariant goes into the rule file whose paths own the code.
- Keep every rule file's paths honest. A rule that matches nothing is a rule nobody loads. The
  routing table in the root is the fallback: read the rule file before planning work in its area
  even if no matching source file has been opened.

A rule file that is wrong is worse than none: kvart's authentication rule file described a
one-year web token while the code had used a 15-minute access token plus role-tiered refresh
since 2026-06-25. The spec bootstrap found it, and it was rewritten before any auth work
`[measured 2026-09-07]`. Doc-vs-code drift in a file that loads into every session is a
priority ticket, not a docs chore.

## Decision records

Repo-level ADRs (structure, contracts, data, security, deployment) live in the code repo.
Team-level ones (rules that hold across a product's repos: money is decimal end to end, API
enum values are English, agents never move money, vote or delete, durable memory lives in the
team-context repo) live in the team-context repo.

Bootstrap: candidates are mined from the existing design documents and confirmed against code
before being written. kvart's bootstrap produced 13 repo ADRs from a candidate table of 30, plus
8 team ADRs, with every evidence path verified `[measured 2026-09-07]`. A decision that cannot
be tied to code is a candidate, not a record.

Format: [templates/adr.md](../templates/adr.md). This repo's own decisions use it too.

## Specs: derived, never hand-edited

Current-state specs describe what the code does today, one feature per file, in business
language, with a technical-references sibling that names the code paths. They are generated:

- **Bootstrap** by retro-generation over the code: mode 1 maps features, mode 2 produces a
  candidate table the owner reviews in the PM role, mode 3 writes the specs. kvart: 3 feature
  maps → 264 candidate slugs → owner review → 20 parallel writers → 247 spec pairs across 20
  subdomains, 5 marked NOT IMPLEMENTED, every folder passing a checker (both files present, every
  cited path exists, no code identifiers in the business spec) `[measured 2026-09-07]`.
- **Kept current** by a sister spec PR on every behaviour-changing code PR (the LEARN edge).

Why before the first ticket: PM skills read specs first and code second. A ticket written
against a repo with no specs forces the agent to reconstruct current state from code on every
ticket, which is the cost specs exist to remove. Day 1 grows by the bootstrap; that is the
honest cost of the standard and a number worth having.

What the bootstrap produced besides specs: a findings file of defects, dead surface and
docs-behind-code, collected from the writers' verified `> Note:` flags. That file became the
ticket backlog for the dogfood cycles. Retro-generation over a real codebase is an audit as a
side effect.

The boundary to keep straight: specs are implemented state; tickets are desired state. A PM
workflow that writes proposed features into `specs/` blurs the two, and a regeneration step
can then faithfully document an unwanted change as if it were the requirement. Proposed,
implemented and released state stay separate.

## Memory: typed claims with a lifecycle

A memory store holds claims of three types (fact, decision, procedure), each with a source,
tags for scope routing, a check-by date, and optional code anchors (file plus blob SHA). Claims
past their check-by date are flagged stale at read time. A reconcile pass finds anchored
memories whose code drifted since they were last verified.

Rules that make it work as infrastructure rather than as a diary:

- Write at the moment of discovery, never at session end. Fixed a bug → correct the fact about
  how the system works. Changed config → supersede the stale claims. Established a workflow →
  write the procedure.
- Search before writing; supersede rather than duplicate. The tool refuses near-duplicates.
- Event-shaped facts ("SHIPPED at commit X") never expire; they record an event. State-shaped
  facts (ports, versions, service inventories) get calendar TTLs and are re-verified at expiry.
- Operator-sourced records are protected: superseding one requires an explicit override that
  is logged into the reason.
- No secrets, no personal data, no session noise in any promoted claim.

Topology: the code repo carries no store of its own, only a config binding it read-only to the
team store. Local writes land in the operator's scratch store under the project's scope.
Durable team knowledge travels by promote PR that the code owner reviews. kvart's 316-record
store moved out of the code repo into the team-context repo with history preserved
`[measured 2026-09-07]`.

The open question the dogfood records: whether a solo owner keeps writing memory under promote
PR friction. Cycles 1 and 2 both wrote to local scratch only and skipped the promote PR
`[measured 2026-09-07]`. What a solo dev drops is what a team must keep, so this is a finding
about the mechanism's friction, not a reason to drop the mechanism.

Commit-time reconciliation: a post-commit hook surfaces memory entries mentioning files the
commit touched. Cycle 1's commit surfaced 7 entries about the changed middleware; all still
true `[measured 2026-09-07]`. The commit is the event that invalidates state facts; decay
catches drift eventually but late.

## The PM workspace

(In full: [14-pm-surface](14-pm-surface.md). The design system as a further layer of the
plane: [15-design-system](15-design-system.md). How the plane is built on Day 1:
[17-onboarding](17-onboarding.md).)

A separate local repository per PM, from a template: intake inbox, discovery notes, features,
ticket drafts, meeting and stakeholder notes, outputs. Its skills read the team-context specs
first and produce tickets scored for readiness. No git operations by the PM; review of specs
flows through the code owner.

What the kvart adoption found: the template's skills hardcode organisation specifics and
reference files the copy did not have, so one skill drafted from the story template alone
`[measured 2026-09-07]`. A template that ships with its lookups broken is a finding for the
template, and it is in the cycle report.

## Team-context repo, minimum shape

```
team-context/
  CLAUDE.md          front door: what the team is, where things are
  CODEOWNERS         specs/** to PM-through-lead, .memspec/** to lead
  docs/adr/          cross-repo decisions
  specs/<subdomain>/<feature>.md + .tech-refs.md
  .memspec/          the durable store
  docs/bootstrap-<date>/findings.md   what retro-generation found
```

Branch protection is the merge gate. On a plan that refuses it (kvart: private repo, free
personal plan, HTTP 403), the gate is a habit: every change lands through a PR the owner reads.
"The gates are mechanics, not etiquette" is the standard's own line, and on that plan they can
only be etiquette. That is a finding the dogfood exists to surface, recorded as a decision
record with the shortcut named.
