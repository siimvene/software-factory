# UX QA Plugin

Behavioral, in-browser QA over the pending diff. The review tier that static code review
doesn't cover: a code-review consort reads the diff, this skill *runs* it.

## Overview

The `qa` skill judges the rendered product the way a careful human tester would, before a
change leaves the working tree:

1. **Scope** — collects the pending diff (unpushed + staged + unstaged + untracked new
   files) and skips runs where nothing user-facing changed.
2. **Surface mapping** — turns changed files into the routes/components/journeys they
   affect: page files → routes, shared components → the pages that render them, i18n files
   → the surfaces using the changed keys (in every changed locale), backend handlers →
   their consuming pages.
3. **Discovery** — resolves how to boot and log into *this* app from the repo's own
   contract (`CLAUDE.md` Commands section, then a run/dev script, then an e2e harness
   config). If nothing answers, it asks once and suggests committing the boot command and a
   test login to `CLAUDE.md`.
4. **Walk** — drives each surface in a real browser via Playwright, checking load, console
   errors, render sanity, the actual diff-touched interaction, and locale rendering, with a
   screenshot per finding.
5. **Report** — severity-ranked findings (CRITICAL / SERIOUS / MINOR) with repro steps and
   screenshots, plus candidates worth codifying as permanent specs.

It reports findings; it does not fix them, and it does not write test specs. Nothing in it
is tied to a specific app, framework, port, or persona: every project-specific value comes
from discovery against the repo.

Runnable in any repo that documents a run command (a `Run:` line or a Commands table in
`CLAUDE.md` is enough). This is a generalization of a skill validated in daily production
use on a real product; the published version is newly generalized, so report any issues
you hit.

## Usage

Ask Claude any of the following, with a UI change pending in your working tree:

```
QA this diff
Walk the UI before I open the PR
Run a UX pass on my changes
Check the frontend renders right
```

When to reach for something else instead:

- Logic / correctness / security review of the code → use a code-review consort, not this.
- Writing or adding automated test specs → not this; this walks the running app.

First run in a repo may ask once for the boot command and a test login; commit those to
`CLAUDE.md` and later runs are zero-question.

## Maintainers

PLG <dev@piletilevi.ee>
