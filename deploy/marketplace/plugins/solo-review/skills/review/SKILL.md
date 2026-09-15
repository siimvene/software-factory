---
name: review
description: Single-model, pack-aware code review that reports findings without applying them. Use for reviewing a diff or branch when the consort cross-model review is unavailable (no Codex on this machine or no OpenAI egress in this environment). If consort is installed and Codex works, prefer /consort:review — one model reviewing alone shares its own blind spots.
version: 0.1.0
---

# review — single-vendor fallback (consort is the standard)

This is the degraded mode. Cross-model review (`/consort:review`) catches what
one model structurally can't see in its own family's output; use this skill
only when the second vendor genuinely isn't available. Say which mode ran in
your report.

## Process

1. **Scope** — default `git diff HEAD` (or `<base>...HEAD` when given a base).
   Note each file's role: source / config / test / infra / docs.
2. **Load the rubric** — resolution order, first match wins:
   1. `PLG_RULE_PACKS` or `CONSORT_RULE_PACKS` (colon-separated files/dirs of
      `.md`/`.mdc`)
   2. repo-local `.claude/rules/` (vendored packs)
   3. the installed plg-rules plugin: newest match of
      `~/.claude/plugins/cache/*/plg-rules/*/rules/` — load `common/`,
      `security/`, and the dirs matching the repo's `activities:` line in
      `AGENTS.md`
   Also load the repo's `AGENTS.md` itself. The packs are the standard; your
   taste is not. If none of the three resolve, say so in the report — an
   unpacked review is opinion-grade.
3. **Inspect** — for each finding record: file, line, severity, title, detail.
   Name the violated pack rule in the title where one applies.
   - **Critical** — security / correctness / data loss
   - **High** — likely bug or significant standard violation
   - **Medium** — maintainability, clarity, missing tests
   - **Low** — style, consistency
4. **Report** — findings ordered by severity, plus what was checked and
   which packs were loaded. State clearly: single-model review, leads not
   verdicts.

## Hard boundaries

- **Never apply your own findings.** Reporting and fixing are separate passes
  with a human decision between them (the fix pass is a fresh, explicit task).
- Never approve, merge, commit, or push.
- If the diff includes `.github/workflows/`, secrets-adjacent files, or auth
  code, flag those findings for human review even at Low severity.
