# PM Workspace Conventions

Convention version: 2.6.0

This file defines how a **Product Manager Workspace** is organised: which folders exist, what goes
into each of them, how documents are named and structured, and how they link to each other.

It is the single shared source of truth for every skill in the `pm-workspace` plugin. Skills must
read this file instead of carrying their own copy of the layout. A copy of this file lives in the
root of every PM workspace, so a workspace stays self-describing even without the plugin installed.

A PM workspace is a **personal** workspace: raw ideas, half-formed hypotheses and dead ends are
allowed to live here. That is deliberate, and it is why nothing leaves the workspace except through
a review gate (see section 15, Graduation). The workspace is not a team repository; it is where the
thinking happens before anything is shared.

---

## 1. Workspace root and paths

- The **workspace root** is the folder that contains this `CONVENTIONS.md`. Everything below is
  described relative to that root.
- Never write an absolute, machine-specific path into a workspace document or into a skill. Paths in
  documents are always relative to the workspace root, so the same workspace works on Windows,
  macOS and Linux.
- To locate the root from anywhere inside the workspace, walk up from the current directory until a
  `CONVENTIONS.md` with a `Convention version:` line is found.

## 2. Convention version

- The line `Convention version: X.Y.Z` near the top of this file is the machine-readable version
  marker. Skills read it with a match on `^Convention version:`.
- The version in the workspace copy tells a skill which conventions that workspace currently
  follows. `pm-workspace-setup` compares it against the plugin's version and upgrades the workspace
  when they differ.
- Bump **patch** for wording, **minor** for a new folder, file or optional section, **major** for a
  change that moves or renames existing content. Record every bump in the changelog (section 18).

## 3. Layout

```
CLAUDE.md            - the rule file (canonical): what this workspace is and how an agent works in it
CONVENTIONS.md       - this file; the layout and writing conventions of this workspace
POINTERS.md          - read-only pointers to code repos and team-context repos (section 13)
TRACKER.md           - the tracker's project, issue types, epic mapping and label table (section 13.1)
SENSITIVITY.md       - what may leave the workspace, and the capture rules (section 14)
_Inbox/              - raw drops before they are filed
Meetings/            - notes from meetings, raw transcripts under Meetings/Raw/
Discovery/           - one document or folder per feature being designed
Features/            - matured features, spec-ready, staged for graduation
Jira/                - staged new issues and issue modifications, before they are applied to Jira
Reference/           - markdown dump of external information related to the work
```

Root registers (the tracking layer, section 11):

```
Todo.md              - active task list
Waiting-On.md        - outstanding asks to other people
Action-Points.md     - commitments captured from meetings
Decisions.md         - global decision log
Ingest-Log.md        - append-only provenance log of ingested sources
```

MAY exist, created only when a workspace needs them:

```
Stakeholders/        - people, roles and stakeholder maps
Templates/           - document and ticket skeletons the agent drafts from
```

Rules:

- These folders cover almost everything. Do not add a top-level folder to fit a single source or
  document. Extend this file first, bump the version, and only then create the folder.
- A layout folder may be absent on surfaces that cannot create empty directories. That is a working
  state, not damage: any skill that files something into a missing layout folder creates the folder
  at write time.
- Subfolders inside the folders above are allowed and expected (see the per-folder sections).
- A workspace may hold extra folders that predate this convention. Skills must leave them alone.
- A workspace may carry an `AGENTS.md` from an earlier version or from the owner's own setup. It is
  preserved as user content; `CLAUDE.md` is the canonical rule file (section 17).

## 4. Naming

- Documents use **Title Case with spaces**: `Localized Emails.md`, `Invoice Fields Extension.md`.
- Meeting notes are prefixed with the date: `YYYY-MM-DD - Topic.md`.
- The root files and registers keep their fixed names exactly as written in section 3
  (`CLAUDE.md`, `CONVENTIONS.md`, `POINTERS.md`, `SENSITIVITY.md`, `Todo.md`, `Waiting-On.md`,
  `Action-Points.md`, `Decisions.md`, `Ingest-Log.md`). Skills match on these names.
- Do not use characters that are illegal in Windows file names: `< > : " / \ | ? *`.
- Keep file names stable. Renaming breaks links from other documents. When a file must move between
  folders (see section 7), it is the moving agent's job to fix the inbound links in the same run.

## 5. Inbox

`_Inbox/` is where loose thoughts and raw inputs land before they are filed: a two-sentence idea, a
pasted note, a source whose home is not yet obvious. Dump first, sort later.

- Nothing stays here. The `ingest` skill files inbox items into the folder they belong in.
- When the type of a source is genuinely unclear, `_Inbox/` is where it lands until the owner
  decides. It is the default landing place, not a permanent home.
- Items that have sat in `_Inbox/` for more than two weeks are worth flagging to the owner.

## 6. Meetings

One file per meeting in `Meetings/`. Raw transcripts and exports go into `Meetings/Raw/` and are
never edited; the readable note is a separate file. `Meetings/Raw/` holds verbatim material and is
kept local only, never committed (see section 14).

```markdown
# YYYY-MM-DD - Topic

**Attendees:** Mari T., Andres K.
**Source:** [link to transcript, recording or `Meetings/Raw/...`]

## Decisions
- ...

## Action points
- AP-ID - action - owner - deadline - status

## Open questions
- Question - owner

## Notes
- ...
```

The **Decisions** and **Action points** sections are mandatory in a processed meeting note. They
roll up into the central registers (`Decisions.md` and `Action-Points.md`, section 11), so nothing
agreed in a meeting lives only in the transcript.

## 7. Discovery

One **feature** equals one document, or one folder when the feature grows beyond a single file.
Discovery is open research: gap analyses, unresolved questions, hypotheses. Stage inside Discovery is
tracked by the `Status` field in the document, not by moving the file around within `Discovery/`.

Every Discovery document carries these four sections. They are the contract other skills rely on:

- **Scope** - what is in, what is explicitly out.
- **Requirements** - what the feature has to do, in business terms.
- **References** - links to external documents, articles, Jira issues, Confluence pages, and to
  files inside `Reference/`.
- **Open questions** - what is unresolved, with an owner per question.

Single-file template:

```markdown
# Feature Name

**Status:** Draft | In discovery | Spec ready | Shipped
**Updated:** YYYY-MM-DD

## Scope
In scope:
- ...

Out of scope:
- ...

## Requirements
- ...

## References
- [Title](relative/path/or/URL) - why it matters

## Open questions
| Question | Owner | Needed by |
| --- | --- | --- |
| ... | ... | ... |
```

When a feature needs a folder, `Discovery/Feature Name/` holds a lead document named after the
feature (`Discovery/Feature Name/Feature Name.md`) that keeps the four sections above and links to
the deeper documents. Deeper documents have whatever structure their content needs.

**Gate rule:** a document reaches `Status: Spec ready` when Scope and Requirements are complete and
no open question blocks the work. Only a `Spec ready` document is ready to move to `Features/`
(section 8), and Jira issues are staged only from `Spec ready` documents.

**Shipped rule:** a shipped feature keeps its document and gets `Status: Shipped`.

## 8. Features

`Features/` holds matured features: one file per feature, spec-ready or in-spec, staged for
graduation. A feature enters `Features/` from `Discovery/` when it is spec-writable, and leaves only
through the `graduate` skill (section 15).

Moving a `Spec ready` document from `Discovery/` to `Features/` is one of the two boundary moves the
workspace allows (the other is `_Inbox/` to its filed home). The agent making the move fixes the
inbound links to that document in the same run, so nothing points at the old location. Everywhere
else, files stay put and stage is tracked by the `Status` field, not by moving the file.

A feature is ready to graduate only when its open decisions and blockers are closed and every claim
about current system behaviour is grounded (section 13, R1).

## 9. Jira

At apply time, expect the target project to enforce **required custom fields the staged
file does not carry** — org accounting fields (Tempo Account, Work for, Capitalisation
Type) are standard across PLG projects. The applying agent reads the create-screen
requirements, asks the owner once for the missing values, and reuses them for the whole
batch; it never guesses cost-attribution values. (Field-proven 2026-08-18: the APT apply
failed on exactly these three until supplied.)

`Jira/` is a staging area. Nothing here has been applied to Jira until its `status` says so, and
nothing is applied without the workspace owner asking for it.

- One subfolder per epic: `Jira/Epic Name/`.
- One file per issue or per modification.
- New issues: `Story - Short Title.md`, `Technical Development - Short Title.md`, `Task - Short Title.md`,
  `Bug - Short Title.md`; the epic's own file is `Epic - Short Title.md` inside its folder.
- Modifications of existing issues: `<ISSUE-KEY> - What changes.md`.

```markdown
---
action: create | update
type: Epic | Story | Technical Development | Task | Bug
key: ABC-123          # only for action: update
epic: ABC-100         # or the epic folder name when the epic itself is not created yet
labels: [flywheel]    # optional; only labels TRACKER.md defines
links:                # optional; "blocks ABC-120", "relates to ABC-119"
status: draft | ready | applied
readiness: 88         # optional; written by readiness-evaluator, 0 to 100
source: Discovery/Feature Name.md
---

# Summary line as it should appear in Jira

## Description
Business-level description of the work.

## Acceptance criteria
- Given ... when ... then ...

## Links
- [Feature Name](../../Discovery/Feature%20Name.md)
```

For `action: update`, the body contains only the fields that change, each under its own heading, and
one line stating why.

`type`, `epic`, `labels` and `links` are worked out by the `ticket` skill from the source document,
the code and `TRACKER.md` (section 13.1), shown with a reason each, and approved with the draft. They
are never asked for as bare values, and assignee, priority, sprint and story points never appear in
a staged file: those belong to the team lead and grooming.

Tickets describe **what**, not **how**: no proposed technical approach sections, and acceptance
criteria state observable outcomes. The developers own the implementation.

`status: ready` is set only when the `readiness-evaluator` skill has scored the file at 85 or
above and the owner has approved marking it ready; no other skill sets that status value.

## 10. Reference

`Reference/` is the markdown dump of information the work depends on: wiki and Confluence pages,
articles from the internet, and content pulled out of spreadsheets and documents received from
colleagues. It describes how things **are today**, not what is being designed. When a claim can be
grounded in code (section 13, R1), it cites where it was checked, and when code and this folder
disagree, the code wins and this folder is corrected.

- One file per source. Subfolders group by topic or system, for example
  `Reference/Legacy/`, `Reference/Markets/`, `Reference/Competitors/`.
- Content converted from a spreadsheet or a text document becomes a markdown table or prose. Binary
  originals are not stored in the workspace.
- Every file starts with provenance, so a reader can tell where the content came from and how stale
  it is:

```markdown
# Title

**Source:** [Confluence page / URL / file received from Mari T.]
**Captured:** YYYY-MM-DD

...content...
```

## 11. Registers (the tracking layer)

Five append-and-maintain files in the workspace root carry the state that used to live in the
owner's head. Skills keep them fresh: `ingest` adds rows from meeting outcomes, and other skills read
them back. Every processed meeting note's **Decisions** and **Action points** sections roll up into
`Decisions.md` and `Action-Points.md`.

| File | What it holds |
| --- | --- |
| `Todo.md` | Active task list, grouped Today / This week / Parked. |
| `Waiting-On.md` | Outstanding asks to someone else that the owner is actively chasing: `ID`, who, what was asked, sent date, last follow-up, status, notes. A follow-up updates the last-follow-up date, not the sent date, so the age of the original ask stays visible. For meeting action points, see the boundary rule below. |
| `Action-Points.md` | Commitments captured from meetings: `AP-ID`, action, owner, deadline, status, origin. An action point without an owner and a deadline is a wish, not an action point; ask for both at capture time. |
| `Decisions.md` | Global decision log, newest first: date, decision, who decided, why (one line), link to context. |
| `Ingest-Log.md` | Append-only provenance log: date, source, type, filed-to, one-line note. One entry per source, not per finding. |

Boundary between the two people-facing registers: a meeting action point owned by someone else stays
in `Action-Points.md` - that is its system of record. Add a `Waiting-On.md` row for it only when the
owner wants an active follow-up loop, and reference the `AP-ID` in that row instead of restating the
action, so one commitment never lives as two diverging descriptions.

Register rows use short sequential IDs (`W-01`, `AP-01`). Closed rows keep their ID and are moved to
an archive section within the same file to keep the active table short.

## 12. Stakeholders and Templates (optional)

Both are MAY folders, created only when a workspace needs them.

- `Stakeholders/` - people, roles, and stakeholder maps per market. Sensitive by default: names and
  roles never go into external queries (section 14).
- `Templates/` - Jira story and epic skeletons and any other document templates the agent drafts
  from. The agent follows these over its own defaults; keep them current.

## 13. POINTERS.md

`POINTERS.md` records where knowledge lives outside the workspace: product code repositories,
team-context repositories, design-standards repositories, and the systems the work depends on (Jira,
Confluence, Figma). Each repository entry names the repository as an `org/repo` slug plus access
notes, never content. A local checkout path may be added where one already exists; it is optional.

- **Everything in `POINTERS.md` is read-only.** The agent reads the repositories through it and never
  writes, commits or pushes to them. The only path from this workspace into a team-context repository
  is graduation (section 15).
- **Read path: connector first.** The default way to read a pointer repository is the workspace's
  GitHub connector, by `org/repo` slug — it works on every surface and needs no git on this machine.
  Where an entry carries a local checkout path and that checkout exists, the agent may grep it
  instead for faster searching; treat a local checkout as possibly stale and prefer the connector
  when freshness matters.
- **Pointer, not copy.** Reading the live repository keeps a single source of truth. Copying spec or
  code content into the workspace forks the truth and lets it go stale.
- **Entries come from discovery, not the owner.** `pm-workspace-setup` fills the repository section by
  searching the GitHub connector for the team's `*-team-context`, `*-team-specs` or `*-context-repo` repository and
  reading the code repositories its `CLAUDE.md` names; the owner only confirms their team. A blank
  placeholder is the fallback for when the connector sees nothing, not the default.

Two hard rules govern how pointer repositories are used:

- **R1 - Ground specs in code.** Before writing any spec claim about current system behaviour, verify
  it in the actual code via a `POINTERS.md` repository and cite where it was checked (repo + path). If
  the code is unreachable or unclear, mark the claim **unverified** rather than presenting a guess as
  current behaviour. Unverified claims become specific questions for the delivery team.
- **R2 - Read/write contract.** Repositories in `POINTERS.md` are read-only. Never write, commit,
  push, or open a pull request against them autonomously. Graduation is the one exception: the agent
  opens the PR only after an explicit go-ahead, and then merges it, because the target context repo
  auto-merges (software-factory adr 0011). The human decision is the go-ahead, not the merge.

### 13.1 TRACKER.md

`TRACKER.md` records how the team's tracker is set up, so that no skill has to ask for it and no
session has to be told twice: the project key and board, the issue types the team uses and what each
is for, how a `Jira/` epic folder maps to an epic key, the labels in use with a meaning and an owner
per label, and the working language of tickets. It is written once by `pm-workspace-setup` (from a
template, filled from the tracker's own metadata where the connector can read it) and corrected in
place from ticket previews.

- **Fields are deduced, shown, approved, never asked twice.** The `ticket` skill reads this file,
  deduces issue type, project, epic parent, labels and links from the source and the code, shows each
  with its reason, and the owner approves or corrects with the draft. A correction that would apply to
  every future ticket (a type rule, a label meaning, a folder's epic key) is offered as an edit to this
  file in the same approval.
- **Only labels in the table are applied.** A label the owner adds by hand in a preview is proposed
  as a new row, with a meaning and who sets it. Labels set by automation (a CI sync, an agent) are
  listed too, marked as never set by the ticket skill, so the skill knows them and leaves them alone.
- **The group's issue-type rules are the default.** A flow a tester or end user can exercise is a
  Story; work that unlocks a capability with nothing visible is a Technical Development (or a Task on
  projects without that type), linked to the stories it blocks; a defect with steps to reproduce is a
  Bug; multi-story scope is an Epic; work outside the engineering workflow is a Task. A team writes
  its own deviations into this file rather than into a skill.
- **Never deduced:** assignee, priority, sprint, story points.

## 14. SENSITIVITY.md

`SENSITIVITY.md` classifies the workspace and decides what may leave it. Fill it in before connecting
the agent to anything external. It marks an overall tier (Public, Internal, Sensitive, Confidential;
Sensitive is the default) and can set per-folder overrides.

The sensitivity gate runs in **both directions**:

- **Outbound.** Before any external query - a web search, a fetch, or pasting workspace content into
  an external tool - check `SENSITIVITY.md`. Material above the tier set there never leaves the
  workspace. At the Sensitive default, external queries are about generic topics only: never include
  company-specific data, names, or figures.
- **Inbound (capture is minimisation).** A workspace that is committed to git keeps its history
  permanently; a committed line cannot be truly deleted. So what gets written into files that outlive
  the conversation is minimised: processed memos carry work outcomes (decisions, action points, asks,
  facts needed for specs), not verbatim quotes. Personal remarks, HR or salary content, and legally or
  commercially privileged passages are not captured; note "sensitive passage omitted, see source"
  instead. Raw transcripts and pulled email or chat content stay in `Meetings/Raw/`, which is kept
  local only and never committed. The mechanism, not just the promise: a git-tracked workspace
  ensures its `.gitignore` contains a `Meetings/Raw/` line (`pm-workspace-setup` adds it when
  missing), and a OneDrive / Cowork setup keeps `Meetings/Raw/` out of any folder shared beyond
  the owner.

## 15. Graduation

Graduation is the single gate out of the workspace. A matured `Features/` document leaves the
personal workspace only as a **pull request into a team-context repository** (`*-team-specs` /
`*-team-context`, `*-context-repo`). The go-ahead to graduate is the human decision: the agent
opens the PR only after an explicit go-ahead, and then merges it automatically, because a context
repo is agent-managed and unread and its PRs auto-merge (software-factory adr 0011). The gate that
keeps half-formed material out of the team layer is the go-ahead plus the checks below, not a human
merge click. Human-owned merge stays the rule for code repositories, which graduation never targets.

Reads out, writes stay in. The agent reads the target repository's spec conventions through
`POINTERS.md`, rewrites the feature into that format, and produces the package. It never pushes
without the go-ahead.

A feature graduates only when every gate check passes:

- **Code-grounded (R1)** - every claim about current behaviour cites repo + path; any unmarked
  unverified claim fails the gate.
- **Decisions closed** - no open decisions or blockers remain; otherwise it goes back to `Discovery/`.
- **Scope traced** - if the feature is part of a larger scope, the parent scope maps this item, with
  no uncovered or undecided flags on it.
- **Sensitivity (both directions, section 14)** - nothing in the package exceeds what the target
  team-context repository may hold. It becomes team-visible; the workspace is not.

The rewritten package lives at `Features/<name>.graduated.md`, next to the feature file it was built
from. This sidecar is a deliberate exemption from the one-file-per-feature rule (section 8) and the
Title Case naming rule (section 4): the `.graduated.md` suffix marks it as a generated artifact, not
a second feature document.

On pass, the agent writes the graduated document into the target repository's format, shows the full
package and its destination, and - only after an explicit go-ahead - opens a pull request through the
GitHub MCP server as the owner's own identity (a feature branch, a single commit of the graduated
file, the PR against the default branch) and then merges it, since the target is an agent-managed
context repo whose PRs auto-merge (adr 0011). There is no local-git or copy-paste route. If the
write or the merge is denied, or the MCP server is unavailable, the agent stops and reports the gap -
it never pastes content by hand and never claims a PR or merge it did not make. The `graduate` skill
carries the full procedure.

## 16. Links between documents

- Always relative markdown links, for example `[Localized Emails](../Discovery/Localized%20Emails.md)`.
  Never wikilinks (`[[...]]`) — they are not CommonMark and render broken on GitHub, which matters
  the moment a document graduates into a team repository PR. A PM may view the workspace in any
  markdown editor (Obsidian included — it renders relative links natively); editors are viewers,
  never a reason to change the link format. (Decided 2026-08-19: wikilink accommodation removed.)
- A new document inside a Discovery folder is linked from that folder's lead document, otherwise it
  is unreachable.
- When a file moves across one of the two allowed boundaries (section 7, section 8), the moving agent
  fixes the inbound links to it in the same run.

## 17. Rule file and writing style

The workspace `CLAUDE.md` is the **canonical rule file**: it says what this workspace is and how an
agent works in it, and it holds the owner's personal preferences, including which language to talk
in. `CLAUDE.md` (and an `AGENTS.md`, if the owner keeps one) wins over this section where they
conflict. An `AGENTS.md` present in the workspace is preserved as user content and is not overwritten.

These are the defaults:

- Documents are written in **English**, whatever language the conversation happens in.
- Use `-` (hyphen), not an em dash.
- **Business level.** Workspace documents are read by product managers, designers and stakeholders,
  not by engineers. Leave out class names, file paths, framework names, backend field names, enum
  values, route patterns and regular expressions. Keep behaviour in plain business terms, plus the
  counts that size the work, the markets and the user roles affected.
- Factual and direct. Short sentences, no marketing voice, no aphorisms.
- Privacy: first name plus the first letter of the surname, for example "Mari T.".
- State what is unresolved as an open question instead of guessing.

## 18. Changelog

| Version | Change | Migration for existing workspaces |
| --- | --- | --- |
| 1.0.0 | First version: `Meetings/`, `Discovery/`, `Jira/`, `Reference/`, `CONVENTIONS.md`, `AGENTS.md`. | Create any missing folder and root file. Nothing is moved or renamed. |
| 2.0.0 | Union with the PLG pm-workspace template: adds `_Inbox/`, `Features/`, `Stakeholders/`, `Templates/`, `POINTERS.md`, `SENSITIVITY.md`, registers (`Todo`/`Waiting-On`/`Action-Points`/`Decisions`); rule file is `CLAUDE.md`; `Ingest Log.md` → `Ingest-Log.md`. | Create missing folders and files; rename `Ingest Log.md`; copy `CLAUDE.md` from template (existing `AGENTS.md` content preserved and pointed to). |
| 2.1.0 | `POINTERS.md` repository entries name an `org/repo` slug; the default read path is the workspace GitHub connector, a local checkout is an optional accelerator (2.0.0 assumed local clones). | Add the `org/repo` slug to each repository entry (`pm-workspace-setup` proposes the missing slug lines on upgrade); existing local paths stay valid as optional accelerators. |
| 2.1.1 | Wording: section 11 draws the `Action-Points.md` / `Waiting-On.md` boundary - someone else's action point stays in Action-Points, a Waiting-On row is added only for an active follow-up loop and references the `AP-ID`. | None. |
| 2.2.0 | Section 15: graduation opens the pull request through the GitHub MCP server as the owner's own identity - feature branch, single commit of the graduated file, PR against the default branch - after the go-ahead. The local-git and web-UI / copy-paste submission routes are removed; a denied write or an unavailable MCP server is an honest stop, never a manual fallback. | None for the workspace layout. PMs need the GitHub MCP server connector authenticated with write scope on the target `*-team-specs` repository; without it, graduation stops and reports the gap. |
| 2.4.0 | Section 9: `type` gains `Technical Development` (the group standard's type for work with nothing visible; Task where a project lacks it). Section 13.1: `TRACKER.md` holds the tracker's project, issue types, epic-folder mapping, label table and working language, written once and corrected from ticket previews. Section 9: staged issue files may carry `labels` and `links`; type, epic, labels and links are deduced by the new `ticket` skill and approved with the draft, never asked for as bare values. | Create `TRACKER.md` from the plugin template when missing (`pm-workspace-setup` fills the project and issue-type rows from the tracker connector where it can and leaves the rest for the owner); never overwrite an existing one. Existing `Jira/` files need no change; `labels` and `links` are optional. |
| 2.3.0 | Section 13: `POINTERS.md` repository entries are populated by discovery. `pm-workspace-setup` searches the GitHub connector for the team's `*-team-context` / `*-team-specs` repository and reads the code repositories its `CLAUDE.md` names; the owner confirms their team rather than pasting slugs. The blank placeholder is the fallback for when the connector sees nothing. | None for existing workspaces. A workspace with an empty `POINTERS.md` gets its repository section offered by discovery on the next setup run. |
| 2.5.0 | Section 9: staged `Jira/` files may carry an optional `readiness` field (0 to 100), written by the new `readiness-evaluator` skill; `status: ready` is set only at a readiness score of 85 or above with the owner's approval. New skills `readiness-evaluator`, `task-improver`, and `task-splitter` score, refine, and split staged tickets without ever writing to Jira. | None; the field is optional. |
| 2.6.0 | Sections 13 and 15: graduation into an agent-managed context repo (`*-team-specs`, `*-team-context`, `*-context-repo`) opens the PR and then **merges it automatically** - the human decision is the go-ahead to graduate, not a merge click (software-factory adr 0011). Human-owned merge unchanged for code repositories. | None for existing workspaces. |
