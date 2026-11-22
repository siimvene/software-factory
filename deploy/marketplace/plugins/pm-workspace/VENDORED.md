# pm-workspace, vendored with one change made here

- Upstream: the group's plugin catalog, `main` @ `ff7c175` (1.9.1), made company-agnostic in the two
  steps `deploy/README.md` describes.
- Version: `1.9.1+sf.1` in `plugin.json` and the marketplace entry. Upstream is `1.9.1`; the suffix
  counts the changes made here. Claude Code caches an install under its version, so a change to
  this copy without a new version never reaches a machine that already installed it.
- One change: GitHub issues as a second tracker kind, conventions 2.9.0. `TRACKER.md` names the kind
  (`jira` or `github`); `references/CONVENTIONS.md` section 13.2 maps the staged ticket format onto
  a repository's issues and a GitHub Project; `ticket`, `apply` and `pm-workspace-setup` follow it.
  Files: `references/CONVENTIONS.md`, `references/TRACKER.template.md`,
  `references/CLAUDE.template.md`, `skills/ticket`, `skills/apply`, `skills/pm-workspace-setup`,
  `skills/ingest`, `skills/readiness-evaluator`, `skills/task-improver`, `README.md`,
  `.claude-plugin/plugin.json`.
- Class: designed. Written 2026-11-22, not yet exercised against a live repository.
- Not offered upstream yet.

To move the pin: copy the tree at the newer upstream commit, apply both scrub steps, re-apply the
change above from the commit that added this file, and update the pin here and in
`deploy/README.md` in the same pull request. If upstream has meanwhile used conventions 2.9.0 for
something else, this change takes the next free minor version and its changelog row moves with it.
