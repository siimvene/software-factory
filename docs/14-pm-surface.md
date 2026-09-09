# The PM surface

The loop starts before any agent touches code. Someone has to turn a finding, a complaint or a
backlog row into a ticket with numbered observable examples that a fleet can build against and a
person can accept on. That work has its own workspace, its own skills and its own gate, and it is
the least automated part of the factory: [02-loop](02-loop.md) says SPEC ends with "a ticket
approved by a person", and this document says what the person and their agent actually work in.

The short version: a per-PM local repository from a template, a catalogue of skills that read the
specs before the code and never write outside the workspace, a numeric readiness rubric with a
threshold, and exactly one gated path out of the workspace into the team layer.
[04-knowledge-plane](04-knowledge-plane.md) covers the four knowledge layers this surface reads
and the one it may propose to; this document does not repeat them.

## The workspace

One local repository per PM, created from a template, cloned next to the read-only clones of the
specs repository and the code repositories. It is a working environment, not a publication: the
design calls it the swamp, because half-formed material is supposed to live somewhere that is not
the team's source of truth.

| Folder or file | Holds | Lifetime |
|---|---|---|
| `_Inbox/` | dropped sources not yet processed | until ingested |
| `discovery/` | research, open questions, gap analysis | until enough is known for a spec |
| `features/` | specs ready for ticket writing | until graduated |
| `<tickets>/` | drafted tickets, one subfolder per epic | until the tracker owns them |
| `Meetings/` | processed memos; `Meetings/Raw/` holds transcripts and pulled mail, git-ignored | memo permanent, raw local only |
| `Stakeholders/` | names and roles | permanent, never in an external query |
| `Decisions.md` | what was actually decided, not discussed | permanent |
| `Action-Points.md` | ID, action, owner, deadline, status | until closed |
| `Waiting-On.md` | outstanding asks with the date sent | until answered |
| `Todo.md`, `Ingest Log.md` | the daily tracking layer | rolling |
| `outputs/` | reports and deliverables | permanent |
| `session-logs/` | one log per refinement session, with score progression | permanent, mined by a skill |
| `reference/` | how things work now, stable knowledge | permanent |
| `templates/` | story, epic and product-spec templates | permanent |
| `POINTERS.md` | where every read-only clone lives and what it answers | permanent |
| `SENSITIVITY.md` | the tier that decides what may leave the machine | permanent |
| `.claude/skills/` | the skill catalogue below | permanent |

Two rules give the workspace its shape.

**The write contract.** The specs repository and the code repositories next to the workspace are
read-only. The agent never writes, commits, pushes or opens a pull request against them. The only
path out is the graduate skill, which prepares a package that the human submits. Half-baked
material stays in the swamp by design, which is what keeps the team layer worth reading.

**Sensitivity in both directions.** Outbound, the tier in `SENSITIVITY.md` decides what may appear
in a web search, a fetch, or anything pasted into an external tool; the default tier is Sensitive,
which means generic topics only and no company-specific data, names or figures. Inbound, capture
is minimisation rather than transcription: a memo carries decisions, action points, asks and
facts, and personal remarks, salary content and privileged passages are omitted with a note
pointing at the source. Raw transcripts stay in the git-ignored folder.

### Why it is a repository the PM never runs git in

The workspace is version-controlled because everything else in the factory is: history, diffs,
recoverable state, and the ability to hand a PM a fresh machine and reproduce their context. It is
not version-controlled so that the PM learns git.

- The PM's job on this surface is judgement, not mechanics. Every git operation the workspace
  needs is either done by the agent inside the workspace or, for the one hop that leaves it,
  offered as two routes: the exact commands, or a click path in the hosting web interface with a
  fallback of sending the package to someone who will submit it.
- Read-only clones are set up once, by whoever runs the adoption, with scoped tokens. The PM never
  refreshes them by hand; if the agent reports a clone stale or unreachable, that is a question to
  ask, not a command to learn.
- The write contract is easier to enforce than to explain. A PM who cannot push cannot push
  half-formed material into the team layer at 23:00, and the gate stays the gate.

The cost is real and worth naming: a PM who never runs git also never sees a merge conflict, so
the agent must surface staleness loudly rather than working from a remembered state.

## The skill catalogue

Seventeen skills, in the shape the kvart adoption ran them. Names here are generic: rename freely,
but keep the firing conditions in the description, because the description is what decides whether
the skill fires at all. Inputs are given in read order, and the order is itself a rule from the
workspace contract: check the spec first, grep the code when the spec is unclear or silent, ask
the human only when the answer is genuinely not determinable from either, and say what was checked.

"Gated" below means the skill refuses to proceed or requires an explicit confirmation before a
write or a promotion. "Advisory" means it produces something a person then decides on.

| Skill | Job | Inputs, in read order | Output artifact | Loop position | Kind |
|---|---|---|---|---|---|
| `ingest` | Pull a source into the workspace and, first, find what the workspace already says about it | the source (file, wiki page, tracker item, URL, code grep), then the whole workspace for existing coverage | an entry in `Ingest Log.md` plus writes into `discovery/`, `reference/` or the tracking files, after confirmation | SPEC intake | gated: shows the plan and writes only on confirmation |
| `analyze` | Produce an exhaustive verified picture of an existing feature or flow, not a partial slice | specs, then code entry points, input classes, configuration types, validators, message bundles, feature flags, then workspace notes | an analysis document in the workspace, every claim citing a path or class | SPEC intake | advisory |
| `architect-review` | Senior-engineer adversarial pass over draft tickets before build starts | the domain's specs, workspace reference and open questions, then the frontend and backend code | findings as BLOCKER, MAJOR or MINOR, each with evidence and a concrete fix | SPEC readiness | advisory, but a BLOCKER is a stop |
| `ticket` | Draft a story or an epic from a source spec | the source file, then the story and epic templates plus the skill's own style rules, then code for gap resolution | a ticket file under the tickets folder, saved only on approval | SPEC intake | gated: refuses an epic without a `features/` spec, blocks on unresolved product decisions, never writes to the tracker |
| `readiness-evaluator` | Score a ticket against a 7-criterion rubric out of 100 | the ticket text, then the domain spec folders, then the workspace notes | a score table, per-criterion gaps with citations, and one highest-impact question | SPEC readiness | gated: below the threshold it hands off to the improver |
| `task-improver` | Conversational refinement loop that raises a weak ticket to the threshold, one question at a time | the ticket, the evaluation output, then the same context sources as the evaluator | a polished ticket, a drift check, and a session log with score progression | SPEC readiness | advisory, with a gated write-back |
| `task-splitter` | Split a ticket that is over about 2 person-days into independently deliverable sub-tasks | the polished ticket only | a split proposal with a coverage check, the parent promoted to an epic | SPEC readiness | gated: proposal, then explicit confirmation before any write |
| `task-degrader` | Degrade a good ticket into a bad one to test the scoring pipeline | a good ticket | a synthetic bad ticket for calibration | LEARN | advisory, test fixture only |
| `improver-optimizer` | Mine the session logs for bottlenecks, drift and stagnation, then propose edits to the improver skill itself | `session-logs/` in bulk | a diagnostic report plus numbered recommendations against the improver's own instructions | LEARN | advisory, applies edits only on request |
| `session-checkpoint` | Save, list, resume and branch a refinement session | the conversation's score tables and question log | a checkpoint file outside the workspace | daily ops | advisory, non-destructive by rule |
| `graduate` | Promote a `features/` file into the team layer | the file, then `POINTERS.md`, then the target repository's spec conventions | a rewritten file plus a handoff package: target path, branch name, title, description, and both submission routes | SPEC to team layer | gated: six checks, all must pass, no partial packages, the human submits |
| `demo` | Build a throwaway clickable prototype as a stakeholder reaction artifact | a discovery or features file, then the design standards, then the code for the behaviour it mirrors | one self-contained HTML file in the discovery folder | SPEC intake | gated by three hard rules: a visible throwaway banner, fake data only, never lands in the team layer. Once the flow is agreed it is attached to the ticket as a design artifact, a load-bearing input for the frontend builder (decided 2026-09-09, not yet measured) |
| `tracker-mcp` | Every read and write against a ticket tracker such as Jira | tracker identifiers and the current user, then the issues themselves | tracker mutations | daily ops and SHIP | gated: preview, confirm, execute on every write |
| `release-note` | Turn shipped tickets into a release page entry | the tickets, grouped by user-visible change | a title plus a two or three sentence factual description | SHIP | advisory |
| `morning` | Start-of-day brief with chase and overdue flags | `Todo.md`, `Waiting-On.md`, `Action-Points.md`, then the tracker if connected | a brief under 25 lines: top three, chase list, overdue, blocked, heads-up | daily ops | advisory |
| `wrap-up` | Persist the session's outcomes so nothing agreed dies in the transcript | the conversation | updates to the four tracking files plus a five-line summary of what landed where | daily ops and LEARN | advisory, but capture is mechanical by rule |
| `onboard` | Set up a new PM's workspace and clone the read-only repositories | answers from the PM, one question at a time | a personalised workspace instruction file and the clones | day 0 | advisory |

Three observations about the catalogue as a whole.

- Only three skills are true gates: `ticket` refuses to draft outside the pipeline, `graduate`
  refuses to package a file that fails any of six checks, and any tracker write is preview and
  confirm. Everything else is a document a person reads. That ratio is correct for this stage:
  the mechanical gates in [05-sensor-stack](05-sensor-stack.md) act on code, and there is no code
  yet.
- The pipeline is enforced for epics and relaxed for single stories. An epic drafted from
  unresolved research is refused with a proposed alternative path; a one-story request from chat
  is allowed. Enforcing the full ladder on every one-liner is how a process gets routed around.
- Two skills exist only to improve the skills. The degrader manufactures bad input, and the
  optimizer reads the session logs and proposes edits to the refinement loop. That is the LEARN
  write-back of [02-loop](02-loop.md) applied to the PM surface rather than to code, and it is the
  part most teams skip.

## The readiness rubric

The evaluator scores one ticket out of 100 across seven weighted criteria.

| Criterion | Points | Full marks means |
|---|---|---|
| Objective or problem statement | 20 | why this exists and what breaks without it, in the ticket itself |
| Acceptance or success criteria | 25 | observable outcomes, not implementation bullets |
| Scope boundary | 15 | in scope and, explicitly, out of scope |
| Actor clarity | 10 | which role or permission drives each flow |
| Pre-conditions and dependencies | 10 | what must be true or shipped first |
| Specificity and concrete examples | 15 | exact values, states and messages rather than adjectives |
| Title clarity | 5 | reads as a user value statement or a clear feature name |

Bands: 85 to 100 is Good and ready for planning, 55 to 84 is Decent with significant gaps and one
refinement round likely, 0 to 54 is Bad and needs a full refinement conversation. **85 is the
threshold**, and it is wired rather than advisory: below it the evaluator hands straight to the
improver without waiting to be asked, and the improver's own target is 85 or better. At or above
it the evaluator always offers three paths (record the evaluation and mark ready, keep improving,
or split) and never picks one itself. That threshold matches the ticket template in
[templates/ticket.md](../templates/ticket.md), which carries the readiness line as a field.

Three scoring principles keep the number honest, and they are the reason it is worth having a
number at all.

- **Document-only scoring.** The score is derived solely from text present in the ticket. A gap
  that would need domain knowledge or an adjacent system to fill is still a gap. The score is a
  claim about the document, not about the feature.
- **No scope widening.** The evaluator does not introduce actors, systems or edge cases the
  ticket never mentioned, and a widening question the author rejects is score-neutral. Without
  this rule the rubric becomes a machine for growing tickets.
- **Context lookup does not move the score.** Before scoring, the skill looks for the matching
  current-state spec first and the workspace notes second. Finding them changes the feedback, not
  the number: a gap becomes "the spec already names the actor, cite it from this path", which is a
  copy rather than a conversation. Nothing found means the rubric is applied unchanged.

A drift check runs on the last iteration only: the final version is compared against the original
input and anything introduced along the way that was not present or clearly implied is listed. It
is a warning, never a score adjustment. That is the same failure the improver loop invites and the
same one a builder-authored acceptance criterion invites, which is why
[07-roles-and-authority](07-roles-and-authority.md) puts acceptance on the requester.

## From intake to ticket

```mermaid
flowchart LR
    S["source: finding, request,<br/>meeting, backlog row"] --> I["ingest<br/>cross-reference first"]
    I --> D["discovery/<br/>open questions"]
    D --> A["analyze<br/>verified current state"]
    A --> F["features/<br/>spec, blockers closed"]
    F --> T["ticket<br/>draft from template"]
    T --> R["readiness-evaluator<br/>score /100"]
    R -->|"below 85"| M["task-improver<br/>one question at a time"]
    M --> R
    R -->|"85+, too big"| P["task-splitter"]
    P --> R
    R -->|"85+"| B["BUILD"]
    F --> G["graduate<br/>six gate checks"]
    G --> H["human submits the PR"]
```

The gate checks that `graduate` runs, all of which must pass, are worth copying verbatim into any
adoption: every claim about current behaviour cites a repository and a path, or is marked
unverified and listed; no open decisions or blockers remain; the parent scope maps this item with
no open flags; any estimate carries base plus contingency plus a justification; the ticket
describes what rather than how and its criteria are observable; and nothing in the file exceeds
what the target team repository may contain. On failure it returns a gap list and no partial
package.

### Three states, three homes

The boundary that makes this pipeline work, and the one most likely to be blurred:

| State | Lives in | Written by | Answers |
|---|---|---|---|
| **Implemented** | the team layer's current-state specs | generated from code, then reviewed | what does the system do today |
| **Desired** | the ticket | the product hat, before build | what changes, and how will we know |
| **Proposed** | the workspace `features/` folder | the PM, thinking out loud | what might we do, if we decide to |

Current-state specs are derived, never hand-edited: they are generated from the code and updated
by a sister pull request attached to the commit that changed the behaviour
([04-knowledge-plane](04-knowledge-plane.md), and adr 0007 in this repository). A ticket is the
delta and nothing else, because the current state is already written down. Proposed work is
neither, and it is the reason the workspace exists as a separate repository at all.

**The trap.** `graduate` rewrites a `features/` file into the target repository's spec format and
prepares a pull request into it. Read that sentence again: a proposal, formatted as a spec,
landing in the directory whose entire contract is "this describes what the code does today".
Nothing in the six gate checks tests for it, because every check is about the file's quality
rather than about which state it represents. Merge that pull request and the layer every future
agent session reads as ground truth now contains a feature that does not exist, indistinguishable
from the ones that do. The next session builds against it, or worse, a spec-versus-code drift
check flags the real code as wrong.

Three defences, cheapest first:

1. Graduate proposals into a proposal area or a decision record, never into the current-state spec
   tree. A proposal that survives becomes a ticket; the spec follows the shipped commit.
2. If a proposal must live in the team repository, mark its state in the file's own front matter
   and make the generator's drift check skip anything not marked implemented.
3. Add a seventh gate check to the skill: name the state this file represents, and refuse a
   current-state target for anything other than implemented. This is the only one of the three
   that is mechanical, and it is a two-line change.

## What the kvart adoption measured

Two cycles on 2026-09-07, both PM stage through to production, both reported in
[the case study](../case-studies/kvart-reference-implementation.md).

| What | Cycle 1 | Cycle 2 |
|---|---|---|
| PM stage wall-clock, first look to ticket drafted and scored | ~11 min `[measured 2026-09-07]` | ~29 min `[measured 2026-09-07]` |
| Readiness, self-scored against the rubric | 94/100 `[measured 2026-09-07]` | 93/100 `[measured 2026-09-07]` |
| Dev hat on to code pull request open | 12 min 11 s | 18 min 58 s |

The PM stage is not the expensive stage, and in cycle 2 it is where the value was. Twenty of those
29 minutes went into reading code, the production database, the production logs and the audit
trail, and they corrected the premise: a ticket that started as "fix a misleading label" became
"retire a payment path" once the investigation showed the section had been invisible since May and
the flag was still writable through the API. A 4-minute intake would have produced a fast, correct,
worthless ticket.

Findings about the surface itself, each one a defect in the template rather than in the product:

- **The drafting skill referenced a file the copy did not have.** Its instructions say to always
  re-read the style rules before drafting, and the style-rules file does not exist in this copy, so
  the ticket was drafted from the story template alone `[measured 2026-09-07]`. A template that
  ships with its own lookups broken fails silently, because a missing reference reads as a skipped
  step rather than an error. The check is mechanical and belongs in the template's own test: for
  every path a skill names, assert it exists.
- **A ticket tracker, which closed a cycle-1 shortcut.** On 2026-09-07 there was no tracker, so the
  stage was a status line in a file `[measured 2026-09-07]`: tickets lived as files in the workspace
  and moved Ready, In Progress, In Test, Ready for LIVE by editing one line, and four of seventeen
  skills (the evaluator's write-back, the improver's write-back, the tracker skill and the splitter's
  write sequence) had nothing to talk to. It was recorded as a cycle-1 shortcut in a decision record
  rather than papered over. That shortcut is now closed: since 2026-09-09 the reference implementation
  runs a real tracker (Jira) `[measured 2026-09-09]`. Pickup assigns the ticket to the loop's account
  and moves it to In Progress; a workflow moves it In Test on PR open with a remote link, Ready for
  LIVE on green CI or merge, and back to In Progress on red; a deploy write-back closes every ticket
  in the deployed range. Keys come from titles, never bodies, and events never move epics. The first
  write-back closed 6 tickets, and the merge leg moved a ticket 13 s after the merge. Still by hand:
  the "decision needed" post from tracker comments to the escalation channel. One rule the tracker
  taught the same evening: a status is not a resolution. The workflow, created over the API with
  statuses and transitions only, left every Done ticket Unresolved (`resolution = Unresolved`
  matched all of them, `resolvedDate` stayed empty, reports counted nothing as resolved). The
  terminal transition needs a post-function that sets Resolution, and the reopen transitions one
  that clears it; a list view with the Resolution column is the check `[measured 2026-09-09]`.
- **Readiness was self-scored** `[measured 2026-09-07]`. The same session that wrote the ticket
  applied the rubric to it, so the number is a self-assessment, and the improver loop, whose whole
  design is a second party asking one question at a time, never ran.
- **The product hat and the builder hat ran in one session, in both cycles** `[measured
  2026-09-07]`. The plan called for separate sessions separated in time. The builder pass therefore
  inherited the author's framing, which is exactly the failure the cross-vendor reviewer exists to
  catch, and in cycle 2 it did: the reviewer found a HIGH defect in a money path that the author's
  own scoping had created.
- **The workspace's `features/` folder was empty in both cycles**, so the team specs plus the code
  plus production stood in as the pipeline source `[measured 2026-09-07]`.

## What a team must keep that a solo owner dropped

A solo owner is both hats, has no tracker, and is their own reviewer, so the shortcuts above are
survivable: the cross-vendor review and the mechanical gates catch what the missing separation
would have caught. None of that transfers to a team, and the list of what has to come back is
short and specific.

1. **Two hats, two sessions, separated in time.** The reason is not tidiness, it is that the
   builder must not inherit the author's framing. A solo owner buys the same property back with a
   non-inheriting reviewer; a team gets it for free by having two people, and should not spend it.
2. **The readiness score comes from someone other than the author.** An evaluator agent that never
   saw the drafting conversation, plus the approving person. A self-score is a useful draft check
   and is not acceptance.
3. **A real tracker, so the stage is not a line in a file.** Everything the tracker skill, the
   write-backs and the split sequence do assumes an addressable ticket with its own history. The
   file-based shortcut worked for one person and stopped working the moment two people disagreed
   about what was in test, so the reference implementation closed it: since 2026-09-09 it runs Jira,
   with pickup, the PR and CI transitions, and a deploy write-back all driven from the loop
   `[measured 2026-09-09]`. What is still by hand is the "decision needed" post from tracker comments
   to the escalation channel.
4. **The improver loop actually running.** One question at a time, against the criterion with the
   most points on the table, with the session log written. The logs are the input to the skill that
   improves the skill, and a workspace with no session logs cannot run that write-back at all.
5. **The graduate gate as the only write path, plus the state check above.** Solo, the code owner
   and the PM are the same person, and the gate degrades into a habit. With more than one PM it is
   the only thing standing between the team's current-state specs and a swamp of proposals.
6. **The sensitivity classification, filled in.** A solo owner writing about their own product can
   leave the default tier and lose nothing. A team workspace holds stakeholder names, vendor
   material and unreleased plans, and the tier is what decides whether any of it may appear in an
   external query. An unfilled classification file defaults to the strictest tier for a reason.
7. **The tracking layer, rolled up.** Decisions, action points with an owner and a deadline,
   waiting-on rows with the date sent, chased at three days. Solo, the loop is short enough to hold
   in one head between sessions. Across a team it is the difference between an agreement and a
   memory of an agreement.
8. **Estimates with a contingency and its justification.** Base plus a percentage, defaulting to 25
   and rising to 50 for fuzzy scope, legacy systems or third-party dependencies. A confident single
   number is the one output of this surface that other people plan around.
