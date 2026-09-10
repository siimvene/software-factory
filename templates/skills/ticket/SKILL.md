---
name: ticket
description: Draft a ticket - story or epic - for the product from a source spec in features/, a chat description for single stories, or context from an existing ticket. Use this skill whenever the user wants to create, draft, write, or scaffold a ticket, story, or epic, including when they say "draft a ticket / epic / story", "create a task", "write a story", or reference a features/ or discovery/ doc and want to turn it into work items. Enforces the discovery → features → tracker pipeline for epics but allows single-story shortcuts from chat. Drafts in chat, saves to the workspace on approval, never pushes to the tracker directly.
---
<!-- Ported from the reference implementation's PM workspace, 2026-09-10. Generic names per docs/14-pm-surface.md; rename freely, but keep the description's firing conditions, because the description is what decides whether the skill fires. -->

# Ticket skill

Draft a ticket (story or epic) for the product. Output to chat, save to the workspace on approval, stop. Never push to the tracker via MCP.

Workspace root: `the workspace root`

## Pipeline rules

discovery → features → tracker. Enforced for epics, relaxed for single stories.

| Input | Story | Epic |
|---|---|---|
| File in `features/` | OK | OK (best path) |
| File in `discovery/` | Ask: skip features/ or promote first? | REFUSE - propose promotion to features/ first |
| Chat description only | OK | REFUSE - propose writing a features/ spec first |
| Existing `<tickets>/` ticket as context | OK (e.g. alt variant of existing) | OK (e.g. follow-up epic) |

If refusing, do not draft. State why and offer the alternative path.

## Inputs accepted

- `/ticket <path>` - explicit path
- `/ticket <name>` - glob in features/ first, then discovery/
- `/ticket <chat description>` - free text (single story only)
- `/ticket` - check conversation context for a recently referenced file or topic; ask if unclear

The triggers above are English. Add your team's own language triggers here.

## Step 1 - Resolve and classify source

Find the source. Classify by location to decide if drafting is allowed (see Pipeline rules table). If the input is chat-only, classify by intent (single story vs epic) - epics need a features/ spec first.

## Step 2 - Read templates and style rules

Always re-read these. They evolve.

- `templates/Story.md` (workspace) - story structure, Title patterns, What to omit
- `templates/Epic.md` (workspace) - epic structure
- `references/style-rules.md` (this skill) - 11 style rules, read before drafting

Workspace templates give structure. Style rules give discipline. On conflict, style rules win (they're more recent corrections).

## Step 3 - Detect mode

- **Single story** - one capability, one user flow
- **Epic + child stories** - multi-capability, multi-deliverable. Draft the epic plus a list of child stories using vertical-slice splits (see style-rules).
- **Both / ambiguous** - ask before drafting

## Step 4 - Classify gaps

Walk through these checks. For each gap, decide where the answer comes from:

1. **Data semantics** - every metric/value/enum the UI shows needs a formula or definition
2. **Side effects** - state-changing actions need a cascade list (emails fired, refunds triggered, reservations expired, POS sessions closed)
3. **Failure modes + user-facing copy** - what does the user see when upstream fails / validation breaks (copy in the team's working language)
4. **Permissions** - which role or permission string gates the action
5. **Timezone / locale** - which timezone the UI renders in; per-market behaviour
6. **Legacy "as is" references** - any "preserves legacy" claim needs a code reference; no naked "as is"
7. **Cross-scope check** - does the rule extend beyond the stated scope

Resolution paths per gap:
- **In the source** - use it
- **Code lookup needed** - PROPOSE to spawn Explore on the specs repo at `~/{{SPECS_REPO}}/` (from CLAUDE.md) or other code repos cloned next to this workspace. Do not auto-spawn - ask first. If user agrees, spawn.
- **Design lookup needed** - ask for the specific design node ID (design MCP available; never just the parent frame)
- **PM decision needed** - list in chat as a question, BLOCK the draft until answered
- **Tech / grooming** (endpoint shape, service ownership, request/response format) - mark `[dev / grooming]`, do NOT block, do NOT include in the ticket

Hard blockers (multiple unresolved PM decisions, incomplete scope) - surface them and STOP. Do not draft a half-baked ticket.

## Step 5 - Draft

Apply all rules from `references/style-rules.md`. Use workspace template structure.

For backend or technically complex stories, append `## Proposed technical approach` after Other information - subsections with specific class/method names from the codebase. Omit by default for UI tasks and straightforward backend behaviour.

## Step 6 - Output to chat, pause

Print the draft. Below it, list any open questions for the PM (gaps couldn't fill from source / code / design).

Wait for explicit approval before saving. Approval phrases: "save", "OK", "looks good", "approve". Add your team's own language triggers here.

Never save without approval.

## Step 7 - Save to the workspace on approval

Target: `<tickets>/<epic-slug>/`

- **Epic**: detect naming convention used in existing `<tickets>/<other-epic>/` folders and follow it. Examples seen: `epic.md`, `00 - Epic.md`, `<Epic Title>.md`. When uncertain, ask.
- **Story under an existing epic**: find the next sequential prefix used in that folder (`01 - `, `02 - `, or `story-01-`, `story-02-`). Match the local convention.
- **Story without an obvious epic**: ask which folder, don't guess.
- **Single chat-only ticket without an epic context**: ask where to save - propose `<tickets>/_loose/` or a topical folder.

Confirm the save path in chat. Stop.

## What this skill does NOT do

- **Push to the tracker via MCP** - never. If the user explicitly asks to create it in the tracker after the save, that's a separate request - handle it then.
- **Edit existing tracker tickets** - if the user wants to update an existing ticket after research, present findings in chat first, ask before touching. (See `feedback_no_tracker_edits_without_ask` memory.)
- **Suggest assignees, priorities, sprint placement, story points** - those are team-lead / grooming decisions.
- **Draft from discovery/ source for epics** - discovery is unresolved research, not ready for tickets. Propose promotion first.
- **Add competitor monitoring context** - separate workflow.
