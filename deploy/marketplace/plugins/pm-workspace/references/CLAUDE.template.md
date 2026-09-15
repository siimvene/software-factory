# CLAUDE.md

This is a **Product Manager Workspace**: a markdown workspace used to gather requirements, analyse
them, and turn them into Jira issues, and to mature ideas until they are ready to be shared with a
team. There is no source code here and nothing to build.

This file is the **canonical rule file** for the workspace. If an `AGENTS.md` also exists here, it is
left untouched - it may be your own content, or boilerplate left over from v1 of the plugin. Personal
preferences in it (language, tone, product context) still apply, but layout and routing follow
[CONVENTIONS.md](CONVENTIONS.md), which supersedes any v1 layout an old `AGENTS.md` describes. This
`CLAUDE.md` is what the plugin manages and what the skills read first.

## Layout and conventions

The layout of this workspace, the structure of each document type, and the writing rules are defined
in [CONVENTIONS.md](CONVENTIONS.md). Read it before creating, moving or renaming anything.

Short version:

- `_Inbox/` - raw drops before they are filed
- `Meetings/` - notes from meetings, raw transcripts under `Meetings/Raw/` (local only, never committed)
- `Discovery/` - one document or folder per feature being designed, each with Scope, Requirements,
  References and Open questions
- `Features/` - matured, spec-ready features, staged for graduation
- `Jira/` - new issues and issue modifications staged before they are applied to Jira
- `Reference/` - markdown dump of external information: wiki pages, articles, content from
  spreadsheets and documents received from colleagues
- `Todo.md`, `Waiting-On.md`, `Action-Points.md`, `Decisions.md`, `Ingest-Log.md` - the tracking layer
- `POINTERS.md` - read-only pointers to code and team-context repositories
- `SENSITIVITY.md` - what may leave the workspace, and the capture rules

`CONVENTIONS.md` is managed by the `pm-workspace` plugin. To upgrade this workspace to a newer
version of the conventions, run the `pm-workspace-setup` skill; do not edit that file by hand.

## How to work here

- You are working with a Product Manager, not a developer. Give concrete recommendations and take a
  position instead of listing options.
- Save produced documents into the folder the conventions point to, and say in your reply where they
  were saved.
- Ask before anything destructive: deleting or overwriting a document, restructuring folders, or
  sending content outside this workspace. Applying staged changes to Jira, and graduating a feature
  into a team-context repository, always need an explicit go-ahead.
- Ground claims about current system behaviour in the code the `POINTERS.md` repositories point to,
  and cite where you looked. If something was not verified, say so instead of presenting it as a fact.
- Respect the sensitivity gate in `SENSITIVITY.md`, in both directions: what may leave the workspace,
  and what is minimised before it is written into a committed file.
- Keep to the scope asked for. If related work looks worth doing, name it rather than doing it.

## Personal preferences

<!-- Add your own preferences below: conversation language, tone, words to avoid, product context,
     which repositories or Jira projects matter. These take precedence over CONVENTIONS.md. -->
