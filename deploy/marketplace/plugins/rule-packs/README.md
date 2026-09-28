# rule-packs

The organisation's **adopted** rule packs, packaged for pack-aware review (consort,
solo-review) and generation-time loading. This copy ships one company-agnostic example,
`rules/common/ci-gates.md`, to show the shape. An adopter replaces it with its own packs.

## Pack shape

One Markdown file per rule set, grouped by activity (`common/`, `security/`, `devops/`,
`backend-<lang>/`, `frontend-<framework>/`), with front matter:

```yaml
pack: common            # the activity directory the file sits in
description: one line a reviewer can cite
maintainer: a named role, never "TBD" once adopted
status: adopted         # only adopted packs ship; drafts stay in the standards repo
source: where the human-readable standard lives
```

**The release filter is the `status:` field.** Only `status: adopted` packs ship here. A
review citing "the standard" must never cite an unvalidated draft.

This is a distribution artifact: the source of truth is the organisation's standards repo
(git, PR review). Packs change upstream and ship as a version bump, never by editing here.

## Usage

`/plugin install rule-packs@<marketplace>`, then:
- **consort / solo-review** discover the packs automatically (plugin-cache glob), or set
  `CONSORT_RULE_PACKS` explicitly.
- Repos vendoring packs at `.claude/rules/` take precedence (consort 0.3.1+ default
  resolution, no variable needed).
