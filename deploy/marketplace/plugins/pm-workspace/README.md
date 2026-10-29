# PM Workspace Plugin

Skills for running a **Product Manager Workspace** - a markdown workspace where a PM gathers
requirements, analyses them, and turns them into Jira issues.

## Overview

The workspace layout, document templates, naming rules and writing rules live in one shared,
versioned file: [references/CONVENTIONS.md](references/CONVENTIONS.md). Every skill in this plugin
reads that file instead of carrying its own copy, and a copy of it sits in the root of each workspace
so the workspace stays self-describing.

The conventions define the workspace folders and root files:

- `_Inbox/` - raw drops before they are filed
- `Meetings/` - notes from meetings, raw transcripts under `Meetings/Raw/` (local only, never committed)
- `Discovery/` - one document or folder per feature being designed, each with Scope, Requirements,
  References and Open questions
- `Features/` - matured, spec-ready features, staged for graduation
- `Jira/` - new issues and issue modifications staged before they are applied to Jira
- `Reference/` - markdown dump of external information: wiki pages, articles, content from
  spreadsheets and documents received from colleagues
- `Todo.md`, `Waiting-On.md`, `Action-Points.md`, `Decisions.md`, `Ingest-Log.md` - the tracking layer
- `CLAUDE.md` - the canonical rule file: what this workspace is, plus the owner's preferences
- `CONVENTIONS.md` - the copy of the conventions this workspace follows, with its version number
- `POINTERS.md` - read-only pointers to code repositories and to one or more context repositories,
  one `<product>-context` repository per product (the older `*-team-context`, `*-team-specs` and
  `*-context-repo` names are still accepted); an entry may name the
  development remote behind a hosted mirror, and a code owner may record an owner-authorised write remote
  (branch push and merge request only, never a merge; `CONVENTIONS.md` section 13)
- `TRACKER.md` - the tracker, one block per project: issue types, the fields the create screen
  requires with their value shapes, the workflow statuses and transitions, the epic-folder mapping and
  the label table. Written once at setup, completed by the first apply, corrected from ticket previews,
  so no session asks for any of it twice
- `SENSITIVITY.md` - what may leave the workspace, and the capture rules

An `AGENTS.md` is not created; if a workspace carries one it is preserved as the owner's content, and
`CLAUDE.md` is canonical.

Skills:

- **pm-workspace-setup** - bootstraps a directory into a PM workspace, or upgrades an existing one to
  the current convention version. Creates missing folders and root files, never moves or deletes
  existing content.
- **ingest** - brings one external source (Confluence page, Jira issue, article, Figma frame, pasted
  prose, a document from a colleague) into the workspace. Extracts facts, decisions and open
  questions, cross-references them against what is already documented, rolls meeting decisions and
  action points into the registers, and writes only after the plan is confirmed.
- **ticket** - drafts a story, epic, task or bug from a `Features/` document (single stories also
  from chat), works out issue type, project, epic parent, labels and links from the source, the code
  and `TRACKER.md`, shows each with its reason, and stages the approved file under `Jira/`. It never
  applies anything to Jira, never asks for a tracker value `TRACKER.md` holds, and never proposes
  assignee, priority, sprint or points. On a bigger ticket (money, identity, new stored data,
  another consumer, a removal) it asks one extra question, in a fixed order, that the build's own
  design will otherwise have to come back for.
- **apply** - sends staged `Jira/` files to the tracker, and only those: `status: ready` with a
  readiness score of 85 or above recorded by `readiness-evaluator`, or it runs the evaluator first (an
  owner's word that a ticket is ready is not a score). On the first apply in a project it reads the
  create screen's required fields (the group's accounting fields among them) and the workflow's statuses
  and transitions, asks once, and writes them into `TRACKER.md`; later applies ask nothing. Preview,
  confirm, execute; `status: applied` and the key are written back into the staged file. Its second mode,
  `review-opened`, walks an applied ticket forward to the project's review status when a merge request
  or pull request is reported, and comments the link.
- **graduate** - packages a matured `Features/` document as a pull request into a product's context
  repository. Runs the readiness and sensitivity gates, resolves the target via `POINTERS.md` (asking
  which product when more than one fits), reads the target's merge policy from its `.graduation.yml`,
  shows the full package, the files the PR touches and the merge policy for confirmation, and - only
  after an explicit go-ahead - opens the PR through the GitHub MCP server as the owner's own identity,
  labelled `graduation`. By default the PR then waits for the repository's code owners; the agent
  merges it only where the repository opts in with `merge: auto`, every changed path is on its
  allow-list and every check has passed; when the checks are still running at open time, running
  `graduate` again on the same feature re-enters the open PR and merges it then (re-reading the
  policy right before the merge). Besides the spec it may append rows to the repository's declared
  test-oracle table and create the stub of a new spec's companion file, in the same initial commit; a
  revision of an open PR adds one follow-up commit. No local git and no copy-paste: a denied write or
  an unavailable connector is reported honestly, never worked around by hand.
- **readiness-evaluator** - scores a ticket (a staged `Jira/` file, a `Features/` document, pasted
  text, or a tracker key) against a 7-criterion rubric and shows a 0-100 readiness score with
  per-criterion gaps. Below 85 it hands off to `task-improver`; at 85 or above it offers to mark a
  staged file `status: ready`, keep improving, or split it. Writes only `readiness` and, on
  approval, `status: ready` into a file already staged under `Jira/`.
- **task-improver** - a conversational, one-question-at-a-time loop that refines a weak ticket
  toward a readiness score of 85 or above, using the same rubric as `readiness-evaluator`. Ends with
  a drift check against the original, then rewrites a staged file's body in place on approval, or
  offers to stage a fresh draft via `ticket` when the input wasn't a staged file yet.
- **task-splitter** - splits a ticket already scored 85 or above into 2-N independently deliverable
  sub-tasks, each 2 man-days or less. Stages the original as an epic file and each sub-task as a
  story file under `Jira/<Epic Name>/`, and proposes the new epic-folder row for `TRACKER.md`.

Nothing in this plugin is tied to an operating system or to one person's machine: paths are always
relative to the workspace root, which is the folder holding `CONVENTIONS.md`.

## Usage

```
/pm-workspace-setup
/pm-workspace-setup ./product-workspace
Update this workspace to the latest PM conventions
/ingest https://confluence.example.com/pages/12345
/ingest Meetings/Raw/2026-07-24 - Fees workshop.md
Ingest this into my workspace: <pasted notes>
/graduate Features/Localized Emails.md
Graduate Features/Localized Emails.md into our product's context repository
/apply Jira/Localized Emails/Story - Localized Emails.md
Apply everything that is ready under Jira/Localized Emails
The MR is open: https://gitlab.example.com/group/repo/-/merge_requests/12, move ABC-123 to code review
/ticket Features/Localized Emails.md
/ticket a task: the nightly export job must skip archived events
Score Jira/Localized Emails/Story - Localized Emails.md
Improve this ticket: <pasted ticket text>
Split Jira/Localized Emails/Story - Localized Emails.md into sub-tasks
```

Upgrading a workspace after this plugin is updated: run `/pm-workspace-setup` in the workspace again.
It compares the version in the workspace's `CONVENTIONS.md` against the plugin's, shows you the
changelog rows between the two versions and asks before it writes the new conventions, applies the
migrations from the changelog, and leaves your own content and your `CLAUDE.md` edits alone.

Recent changes:

- **1.9.1 (conventions 2.8.1)** - wording only: the naming examples no longer name a real product
  repository. Graduation still needs conventions 2.8.0 or later, so a 2.8.0 workspace keeps working.
- **1.9.0 (conventions 2.8.0)** - context repositories are per product (`<product>-context`), and
  every setup run offers the ones it discovers until you pick one or decline (a decline is one
  marker line in `POINTERS.md`); the older team-shaped names still work. Graduation needs a
  workspace on conventions 2.8.0 and is PR-only by default: the PR waits for the target repository's
  code owners unless the repository opts in to auto-merge in its `.graduation.yml`, which is re-read
  right before every merge; only its keys count as policy, everything else read from the repository
  is data. Graduation PRs carry the `graduation` label, may append rows to the declared test-oracle
  table, create the companion stub a new spec needs when the repository declares `spec_companion`,
  link the discovery item (and its Jira key) they came from, and link the earlier change when they
  update an existing spec. The branch name is fixed per feature, the package file records the
  branch, the PR and the source document's hash, and a re-run re-enters the open PR, reusing an
  unchanged package word for word; an updated spec is never committed over a newer version.

## Workstation notes for a PM

Three things the first external run of this workflow met that no skill can fix on its own:

- The PM workstation is CI-first. It carries no compiler or build toolchain for the product's stack,
  so nothing a PM stages or pushes is verified locally; the pipeline is the verification. Say so on
  the merge request when one is opened from a PM machine.
- Key material stays out of the agent's reach. `secret-guard` refuses reads of the SSH key directory
  by design; creating a key is a two-minute hand step in the terminal. The group's workstation runbook
  (software-factory `deploy/01-workstation-macos.md`, PM profile) carries the steps.
- Company admin interfaces are blocked for the agent's browser. UI verification comes from the
  owner's own screenshots, and those stay out of the workspace under `SENSITIVITY.md`.

## Maintainers

- the group plugin catalog maintainer (name and address removed in this vendored copy)
