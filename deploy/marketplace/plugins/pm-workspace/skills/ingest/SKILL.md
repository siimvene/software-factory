---
name: ingest
description: Use this skill when the user wants to bring an external source into their PM workspace - e.g. "ingest this Confluence page", "add these meeting notes to the workspace", "file this article under Reference", "process this in my inbox", "co z tym zrobić w vaulcie". Extracts facts, decisions and open questions from the source, cross-references them against what the workspace already documents, rolls meeting decisions and action points into the registers, and writes only after the user confirms the plan. Do not use it to file analysis Claude itself just produced, and do not use it to set up the workspace structure - that is the `pm-workspace-setup` skill.
version: 1.1.1
---

# Ingest a source into the PM workspace

Bring one external source into the workspace. Cross-reference it against what is already documented,
propose where it fits, and write only after explicit confirmation.

The pain this solves: "it was already figured out somewhere, but I can't remember where." Finding the
existing knowledge **before** writing new content is this skill's main job, not a side step.

## Workspace layout

Do not assume a layout. Locate the workspace root by walking up from the current working directory
until a `CONVENTIONS.md` containing a `Convention version:` line is found, then read that file. It
defines the folders, the document templates, the naming rules, the linking style and the writing
rules that everything below relies on.

If no `CONVENTIONS.md` is found, stop and say that this directory is not a PM workspace; offer to run
the `pm-workspace-setup` skill. Read the workspace copy, not the plugin's copy at
`$CLAUDE_PLUGIN_ROOT/references/CONVENTIONS.md` - a workspace may be on an older convention version,
and its own copy is what its content follows.

The workspace `CLAUDE.md` is the canonical rule file; read it first. An `AGENTS.md`, if the workspace
still carries one, is a legacy fallback - read it too, but scope what it wins: it takes precedence
only for personal preferences (language, tone, product context). In a workspace upgraded from v1,
`AGENTS.md` may be old plugin boilerplate that describes the v1 layout; layout and routing always
follow the workspace `CONVENTIONS.md`, never a legacy `AGENTS.md`.

All paths handled in this skill are relative to the workspace root, so the same instructions work on
Windows, macOS and Linux.

## Source types and how to fetch them

| Source | How to fetch |
| --- | --- |
| A file already inside the workspace | Read tool |
| Confluence page (URL or page ID) | Atlassian MCP tool for reading a Confluence page, in markdown format |
| Jira issue (by key) | Atlassian MCP tool for a JQL search, with `key = <KEY>` |
| External URL: article, gist, public doc | WebFetch |
| Figma frame | Figma MCP tool for design context |
| Spreadsheet or text document from a colleague | Read tool if a converted or text form exists, otherwise ask the user to export it to text or markdown |
| Prose pasted into the conversation, or a claim the user makes verbally | Treat the input itself as the source |
| A finding in source code | Read the repositories `POINTERS.md` (or the workspace `CLAUDE.md`, legacy `AGENTS.md`) names via the GitHub connector by `org/repo` slug; a local checkout may be grepped to locate code faster, but treat it as possibly stale |

If the source type is not clear from the user's input, ask once with AskUserQuestion. Do not guess.

Ingest one source per run. Several sources means several runs.

## Workflow

### Step 1 - Fetch and extract

Read the source and pull out three things only:

- **Facts** - what is claimed about how the product, market or process works
- **Decisions** - what someone chose to do, or not to do
- **Open questions** - what is explicitly unresolved

Drop narrative, opinions without a basis, and anything that is only context for the reader. Be
aggressive about cutting.

### Step 2 - Cross-reference against the workspace (the high-value step)

For each fact and decision, find what already exists:

1. Check the memory files for this workspace, if there are any, for a topic-to-file map.
2. Grep the workspace for keywords from the finding.
3. Grep the folders the conventions list, starting with `Reference/` and `Discovery/`, then
   `Meetings/` and `Jira/`.

Verify claims rather than trusting them:

- A claim about a Jira issue: read the issue and check it actually says that.
- A claim about behaviour in code: check the repositories named in `POINTERS.md` (or the workspace
  `CLAUDE.md`, legacy `AGENTS.md`) via the GitHub connector. A local checkout may help locate the
  right files, but a possibly stale clone does not count as verification — confirm via the connector.
  If the repository is unreachable, say the claim is unverified.

Do not trust the source uncritically. If the source contradicts the code, the code wins. If two
stakeholders disagree, flag it - never silently pick one.

### Step 3 - Classify each finding

| Status | Meaning | Action |
| --- | --- | --- |
| DUPLICATE | Already documented, same claim | Skip, mention it in the log only |
| UPDATE | Extends or contradicts an existing document | Propose an edit to that document |
| NEW | Novel topic, no related document | Propose where to file it, per the conventions |
| CONFLICT | Contradicts an existing claim and it is not clear which is right | Flag it, ask which one is canonical |

Route a NEW finding by what it is, not by where it came from: how something works today goes to
`Reference/`, a feature being designed goes to `Discovery/`, a matured spec-ready feature goes to
`Features/`, what was said in a meeting goes to `Meetings/`, work to be created or changed in Jira
goes to `Jira/`. When the type of the source is genuinely unclear and no folder fits yet, drop it in
`_Inbox/` for the owner to sort - that is the default landing place, not a guess.

Meeting outcomes route into the registers, not just the memo:

- Each **decision** rolls up into `Decisions.md`.
- Each **action point** (`AP-ID - action - owner - deadline - status`) rolls up into
  `Action-Points.md`. An action point missing an owner or a deadline is a wish, not an action point;
  ask for both rather than inventing them.
- A new ask to someone else that is not a meeting action point goes into `Waiting-On.md` with
  today's date. An action point owned by someone else lives in `Action-Points.md` only; do not
  silently mirror it. Offer a `Waiting-On.md` row (referencing its `AP-ID`, not restating the
  action) when it looks like something the owner will need to chase (conventions section 11).

### Step 4 - Show the plan before writing

```
## Ingestion: [source title or URL]

**Source:** [type, link, who and when if known]

### Extracted
**Facts:**
- ...
**Decisions:**
- ...
**Open questions:**
- ...

### Cross-reference
| Finding | Existing document | Status |
|---|---|---|
| X | Pricing model | DUPLICATE |
| Y | Reference/Markets | UPDATE - extends the EE row |
| Z | (none) | NEW - propose Reference/<Topic>.md |
| W | Reference/Markets (line 42) | CONFLICT - source says 23%, workspace says 8% |

### Proposed actions
1. Update Pricing model, section "Discount logic", with finding Y
2. New file Reference/<Topic>.md for finding Z
3. Roll decisions into Decisions.md, action points into Action-Points.md, new asks into Waiting-On.md
4. Append an entry to Ingest-Log.md

### Need a decision from you
- W (CONFLICT): which one is canonical?
- Z: Reference or Discovery? I would say Reference because [reason], but check me.
```

Reference documents in this report the way the conventions say to link them.

Then **wait**. Write nothing yet.

### Step 5 - Execute after confirmation

Once the user confirms or adjusts the plan:

- Apply the edits and create the new files, following the templates and naming rules in
  `CONVENTIONS.md`.
- A new document inside a Discovery folder gets linked from that folder's lead document, otherwise
  nobody will find it.
- Roll meeting outcomes into the registers: decisions into `Decisions.md`, action points into
  `Action-Points.md`, new asks into `Waiting-On.md`. Create a register only if it is missing.
- Append one entry to `Ingest-Log.md` in the workspace root, creating the file if it is missing. (A
  workspace still on the pre-2.0.0 `Ingest Log.md` name: append to that file and leave the rename to
  `pm-workspace-setup`; do not create a second log.)

```markdown
## YYYY-MM-DD - [source title]

**Source:** [link or workspace-relative path]
**Files touched:** [links]
**Key claims:**
- ...
**Open questions:**
- ...
```

- Confirm what was done in two or three lines, naming every file touched.

## What not to do

- Do not ingest your own analysis. Ingest external sources, not summaries just generated in this
  conversation.
- Do not write before the plan is confirmed. The cross-reference report is the deliverable; writes
  are step 5.
- Do not pad the log. One entry per source, not per finding.
- Do not restructure the workspace to fit the source. Make the source fit the existing structure.
- Do not create a top-level folder. The folders in `CONVENTIONS.md` cover almost everything; if one
  is genuinely missing, that is a change to the conventions, not something to improvise here.
- Do not put an absolute or machine-specific path into a workspace document.
