# TRACKER.md

The team's tracker, as the skills need it. Written once at setup, corrected in place when a ticket
preview shows a field that needed a different answer. Nothing here is asked for again once it is here.

## Project

| Key | Site | Board | Note |
|---|---|---|---|
| `{{PROJECT_KEY}}` | `{{SITE_URL}}` | {{BOARD}} | company-managed / team-managed; which statuses the team uses |

## Issue types in use

The group standard defines Initiative, Epic, Story, Technical Development, Bug, Sub-task, and a Task
type outside the engineering workflow. List the ones this project actually has and what each is for.

| Type | Used for | Note |
|---|---|---|
| Epic | multi-story scope; one `Jira/<Epic Name>/` folder | |
| Story | a user-visible flow a tester or end user can exercise | default for `Features/` sources |
| Technical Development | unlocks a capability with nothing visible; linked to the stories it blocks | use Task if the project has no such type |
| Bug | a defect with steps to reproduce | relates to the story that shipped the behaviour |
| Task | work outside the engineering workflow | |

## Epic parent convention

A story staged under `Jira/<Epic Name>/` gets the epic key in this table. `none` means the folder is a
grouping only and its stories are parentless. A story with no folder is asked once. A new epic in the
tracker is a new row here, in the same approval as the ticket that created it.

| Folder | Epic key | Note |
|---|---|---|
| | | |

## Labels

Only labels in this table are applied. A label added by hand in a preview is proposed as a new row.

| Label | Meaning | Set by |
|---|---|---|
| | | |

## Working language

Titles and bodies in {{LANGUAGE}}; user-facing copy quoted in the product's language where the UI
shows it. Vocabulary follows the code and the team's glossary, not the source document.
