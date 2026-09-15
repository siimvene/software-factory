---
name: pm-workspace-setup
description: Use this skill when the user wants to create, bootstrap, or upgrade a Product Manager workspace - e.g. "set up a PM workspace here", "bootstrap a product manager workspace in ./my-vault", "update this workspace to the latest PM conventions", "check whether my workspace follows the current conventions". Creates the _Inbox / Meetings / Discovery / Features / Jira / Reference structure plus CLAUDE.md, CONVENTIONS.md, POINTERS.md, SENSITIVITY.md and the tracking registers, or upgrades an existing workspace to the current convention version. Do not use it to write feature documents or to ingest sources - that is the `ingest` skill.
version: 1.2.0
---

# Set up or upgrade a PM Workspace

Bring a directory up to the current **PM Workspace conventions**: the folders a Product Manager works
in, the root files that describe them, and the convention version marker that lets a workspace be
upgraded later.

The conventions are not repeated here. They live in `$CLAUDE_PLUGIN_ROOT/references/CONVENTIONS.md`,
which is also the file that gets copied into the workspace. That copy is the shared source of truth
for every skill in this plugin.

`$CLAUDE_PLUGIN_ROOT` is the plugin's own directory, provided by Claude Code. If the variable is not
set, resolve the two reference files relative to this `SKILL.md` instead: `../../references/`.

**Argument** (optional): the target directory, absolute or relative to the current working directory.
With no argument, the target is the current working directory.

On surfaces where the session can see both a connected local folder and its own cloud workspace
(Claude Desktop / Cowork), the PM workspace lives in the **connected local folder**: resolve "here"
to that folder and confirm it by name. Never default to the session's cloud workspace - a PM
workspace bootstrapped there is invisible to the owner's file system and breaks the local-files
model. When the session has no connected local folder at all, do not bootstrap into the cloud
workspace on your own: say that a PM workspace belongs in a folder on the owner's machine, ask them
to connect one, and proceed in the cloud workspace only on their explicit say-so.

## Files this skill manages

| Path in the workspace | Source | On bootstrap | On upgrade |
| --- | --- | --- | --- |
| `CONVENTIONS.md` | verbatim copy of `$CLAUDE_PLUGIN_ROOT/references/CONVENTIONS.md` | create | overwrite - this file is plugin-owned |
| `CLAUDE.md` | `$CLAUDE_PLUGIN_ROOT/references/CLAUDE.template.md` | create | leave user content alone, only add missing pointers |
| `POINTERS.md` | see `CONVENTIONS.md` section 13 | fill the repository section by discovery (step 4a); placeholder only if discovery finds nothing | create only if missing; never overwrite repository entries. Exception: on upgrade to conventions ≥ 2.1.0, if a `POINTERS.md` repository entry lacks an `org/repo` slug, propose the slug lines and add them only with the owner's confirmation (append to entries, change nothing else) |
| `SENSITIVITY.md` | see `CONVENTIONS.md` section 14 | create a placeholder for the owner to fill | create only if missing; never overwrite a filled-in file |
| `TRACKER.md` | `$CLAUDE_PLUGIN_ROOT/references/TRACKER.template.md`, see `CONVENTIONS.md` section 13.1 | create from the template; fill the project and issue-type rows from the tracker connector when it can read the project (step 4b), leave the epic mapping and labels for the owner | create if missing (the 2.4.0 migration); on a re-run, fill only rows that still hold a `{{...}}` template placeholder (step 4b) and leave every filled row as it is. Corrections to filled rows come from ticket previews, not from setup |
| `_Inbox/`, `Meetings/`, `Discovery/`, `Features/`, `Jira/`, `Reference/` | see `CONVENTIONS.md` § Layout | create (defer to first write when the surface cannot create empty folders - step 4) | create only the ones missing (same deferral applies) |
| `Todo.md`, `Waiting-On.md`, `Action-Points.md`, `Decisions.md`, `Ingest-Log.md` | see `CONVENTIONS.md` § Registers | create empty registers | create only the ones missing; never overwrite one that has rows |

An `AGENTS.md` is **not** created. `CLAUDE.md` is the canonical rule file. If a workspace already
carries an `AGENTS.md` (from an earlier version or the owner's own setup), leave it exactly as it is -
its pointer duty is absorbed by `CLAUDE.md`. Do not delete it and do not rewrite it. On upgrade,
check whether the `AGENTS.md` matches the old v1 plugin template (recognisable by the v1 layout: a
"Short version" list of only `Meetings/`, `Discovery/`, `Jira/`, `Reference/`, and no `_Inbox/` or
`Features/`). If it does, tell the owner it is v1 plugin boilerplate now superseded by `CLAUDE.md`
and `CONVENTIONS.md`, and offer to remove or archive it - but only offer; never remove it without
the owner's say-so.

The `Stakeholders/` and `Templates/` folders are MAY: never create them on bootstrap or upgrade, and
leave them alone if they are already present. Create one only when the owner asks for it.

Never delete, move or rename anything that already exists in the target directory, and never touch
folders the conventions do not mention. The one rename an upgrade may perform is the changelog
migration `Ingest Log.md` -> `Ingest-Log.md` (see step 4).

## Steps

### 1. Resolve the target and read the current conventions

- Resolve the target directory. If it does not exist, plan to create it.
- Read `$CLAUDE_PLUGIN_ROOT/references/CONVENTIONS.md` and take the plugin's convention version from the
  `Convention version:` line.
- Read the layout section of that file. The folders and root files to create come from there, not
  from this skill, so a convention bump does not require editing this file.

### 2. Detect the mode

- **Bootstrap** - the target has no `CONVENTIONS.md`.
- **Upgrade** - the target has a `CONVENTIONS.md`. Read its `Convention version:` line and compare
  with the plugin's version:
  - same version - the workspace is current; still check for missing folders and root files, since
    they may have been deleted.
  - workspace version lower - read the changelog section of the plugin's `CONVENTIONS.md` and collect
    every migration listed for the versions in between.
  - workspace version higher, or no version line found - do not write anything. Report it and ask the
    user how to proceed; the workspace may come from a newer plugin or may not be a PM workspace.

Before writing in bootstrap mode into a directory that already holds files but no `CONVENTIONS.md`,
say what is already there and confirm with the user that this is the directory they meant.

### 3. Present the plan

List, in this order:

- resolved target directory
- mode, plus both convention versions when upgrading
- folders to create, and folders already present
- root files to create, overwrite or leave as they are
- migrations from the changelog that apply

Apply the plan without a confirmation round when it only creates missing folders and files, or when
it replaces a `CONVENTIONS.md` whose version is older than the plugin's - that is the upgrade the user
asked for, and the file is plugin-owned. Ask for a go-ahead only when:

- the workspace version equals the plugin's but the content differs, which means somebody edited the
  workspace copy by hand and the edit is about to be lost, or
- an existing `CLAUDE.md` needs a section appended, or
- an `Ingest Log.md` (old name) is about to be renamed to `Ingest-Log.md`, or
- the target already holds files but no `CONVENTIONS.md` (see step 2).

### 4. Apply

- Create the target directory if needed, then each missing folder from the layout.
- When the surface cannot create empty directories (for example the device shell is unavailable), do
  not drop placeholder files into folders to force them into existence. Defer instead: list the
  deferred folders in the report and note that the first skill that files something into one of them
  creates it on write. Offer a retry for when the shell is back, but treat the deferral as a working
  state, not a failure.
- If the workspace is git-tracked (a `.git` directory exists at or above the workspace root), ensure
  `.gitignore` in the workspace root contains a `Meetings/Raw/` line: create the file with that line
  when missing, append the line when the file exists without it, and leave the rest of the file
  untouched. Skip this entirely when the workspace is not git-tracked.
- Write `CONVENTIONS.md` as a byte-for-byte copy of the plugin's file. Do not summarise or reflow it -
  skills and the version check depend on its exact content.
- `CLAUDE.md`:
  - missing - copy `$CLAUDE_PLUGIN_ROOT/references/CLAUDE.template.md`.
  - present - keep every line the user wrote. Add only what is missing: the statement that this is a
    PM workspace, and the pointer to `CONVENTIONS.md` as the definition of the layout. Append a short
    section rather than rewriting existing prose.
  - Never create or rewrite `AGENTS.md`. If one exists, leave it untouched - `CLAUDE.md` is canonical
    and absorbs the pointer duty.
- `POINTERS.md`: when the file is **missing**, do not just drop a blank placeholder - try to fill
  the repository section by discovery first (step 4a). When the file **already exists**, never
  overwrite it: leave every existing line (repository entries and any other pointers the owner added,
  such as Jira or Confluence) untouched. The only edit allowed to an existing file is discovery
  *appending* repository entries when its repository section is empty, and the 2.1.0 migration below.
  One exception for the 2.1.0 migration: when a filled-in `POINTERS.md` has repository entries without
  an `org/repo` slug, work out the slugs (from the entry's URL, local path, or by asking), show them
  to the owner, and append them to the entries only after confirmation.
- `SENSITIVITY.md`: create a placeholder for the owner to fill (from `CONVENTIONS.md` section 14)
  only when missing. Never overwrite one that already has content.
- `TRACKER.md`: when missing, copy `$CLAUDE_PLUGIN_ROOT/references/TRACKER.template.md` and fill what
  the tracker connector can tell you (step 4b). When present, the only edit allowed is replacing a
  `{{...}}` template placeholder that is still there (step 4b on a re-run); every filled row stays as
  it is. The `ticket` skill corrects filled rows from previews, setup does not.
- Registers (`Todo.md`, `Waiting-On.md`, `Action-Points.md`, `Decisions.md`, `Ingest-Log.md`): create
  an empty register only when it is missing. Never overwrite one that has rows.
- Migration rename: if the workspace carries an `Ingest Log.md` (the pre-2.0.0 name) and no
  `Ingest-Log.md`, rename it to `Ingest-Log.md` and fix any inbound links. If both exist, do not
  touch either; flag it for the owner.
- Create nothing else. Templates for documents are inside `CONVENTIONS.md`; do not scatter copies of
  them across the workspace, and do not create placeholder feature documents inside the empty folders.

### 4a. Populate POINTERS.md by discovery

The point of this step is that the owner never has to know a repository slug. Fill the repository
section of `POINTERS.md` from what the GitHub connector can already see. Run this only when
`POINTERS.md` is missing, or exists with an empty repository section; if the file already has
repository entries, skip discovery entirely and leave the file untouched.

Everything here is read-only discovery. You are reading repositories the owner already has access to
through their own connector; no workspace content leaves the workspace, so this is not an outbound
external query and the `SENSITIVITY.md` outbound gate does not apply. Never write, commit, or push to
any repository you discover (R2).

1. **Check the connector, then find the team-context repository.** First establish whether the GitHub
   connector tools are actually available and authenticated in this session. If they are not, stop
   here: state plainly that discovery needs the GitHub connector connected (step 3 of onboarding),
   leave `POINTERS.md` as a blank placeholder when the file is missing, and offer to re-run discovery
   once it is connected. Do not guess why - only report "connector not available" when that is what
   you observed.
   If the connector is available, search the `Piletilevi` organization for repositories whose names
   end in `-team-context` or `-team-specs`. List only what the connector actually returns - never
   invent or guess a repository name.
   - Search succeeded but returned no match: the owner's team is not onboarded yet. Leave a blank
     placeholder when the file is missing, say plainly that a developer sets up the team-context
     repository first, and offer to re-run discovery later.
   - One or more returned: show the owner the list and ask which repository is their team's. Confirm
     even when there is only one match; do not assume.
2. **Resolve the code repositories.** Read the chosen team-context repository's `CLAUDE.md` through
   the connector and take the implementing code repositories it names (as `org/repo` slugs or GitHub
   URLs). Add only repositories the file actually names. If it names none, or cannot be read, record
   the team-context repository alone and note that code repositories are unresolved - specs are the
   main value and the owner can add code repositories later.
3. **Write the entries.** Write the confirmed repositories into `POINTERS.md` as `org/repo` slugs
   under their sections (team-context, then product code), following section 13 - read-only, no local
   paths. Show the owner exactly what was written. The org design-system repository, if the team uses
   one, is an optional manual add; do not guess its name.

### 4b. Fill TRACKER.md from the tracker

Run this when `TRACKER.md` was just created from the template, or exists with `{{...}}` placeholders
still in it (the connector was not available last time). Fill placeholders only; never change a
filled row. Read-only discovery, as in 4a; nothing leaves the workspace.

1. **Check the Atlassian connector.** If its tools are not available in this session, still do
   step 5 (no connector needed), leave the other placeholders in place, say so plainly, and offer to
   re-run once it is connected: the re-run fills only what is still a placeholder.
2. **Project.** Ask the owner which Jira project is their team's (list what the connector returns for
   their account; confirm even a single match). Fill the key, site and board rows.
3. **Issue types.** Read the project's issue types through the connector and keep only the rows in the
   template's type table that the project actually has; note whether Technical Development exists or
   Task stands in for it.
4. **Labels in use.** Read the labels present on the project's open issues. Do not put them in the
   table unfilled: list them to the owner and add only the ones the owner gives a meaning and an
   owner for. The rest stay out until a ticket preview brings them back.
5. **Working language.** One question to the owner: the language tickets are written in. If
   `CLAUDE.md`'s personal preferences already name a conversation or ticket language, propose that
   and confirm. Replace `{{LANGUAGE}}` with the answer; this step needs no connector.
6. **Epic mapping.** Leave blank. Folders under `Jira/` and their epic keys are added by the `ticket`
   skill the first time a story is staged under each folder.

Show the owner exactly what was written.

### 5. Report

State the resolved target directory, the convention version the workspace is now on, and three
lists: created, updated, left unchanged. If the user's `CLAUDE.md` was extended, quote the section
that was appended. State what discovery wrote into `POINTERS.md` (the team-context repository and any
code repositories resolved), or that it fell back to a placeholder and why. State whether `TRACKER.md`
was created and which rows were filled from the tracker. Close with the one thing
worth doing next: fill in `SENSITIVITY.md`, confirm the discovered repositories, or the personal
preferences section of `CLAUDE.md`.

## Rules

- Cross-platform: build paths by joining the target directory with the names from the layout. Never
  hardcode a path separator, a drive letter, or a home directory, and never write an absolute path
  into a workspace file.
- The convention version in the workspace copy of `CONVENTIONS.md` is the only record of which
  conventions a workspace follows. It must always match the file's actual content.
- If the conventions themselves need to change, the change belongs in
  `$CLAUDE_PLUGIN_ROOT/references/CONVENTIONS.md` with a version bump and a changelog row - not in this skill.
