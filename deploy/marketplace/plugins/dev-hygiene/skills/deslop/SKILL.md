---
name: deslop
description: Simplify and de-slop recently modified code while preserving exact behavior. Use when cleaning up AI-generated code after a task, when the user says deslop, simplify, cleanup, or AI slop, or as a finishing pass before a PR. Do not use for refactors that change behavior or for hunting bugs — that's review's job.
version: 0.1.0
---

# deslop — behavior-preserving cleanup of recent changes

Scope: recently modified files (session context, else `git diff` +
`git diff --cached`, else branch vs `main`). Never touch unrelated files;
never revert the user's changes.

## Checklist (preserve behavior exactly)

- Remove comments that narrate code; keep ones explaining non-obvious constraints.
- Remove defensive checks on already-validated paths and null checks types
  already guarantee.
- Replace `any`/needless `unknown` with proper types where the type is clear.
- Remove wrappers, abstractions, and variables that add no clarity.
- One semantic name per concept across touched code.
- Flatten needless nesting; no nested ternaries — prefer `if`/`switch`.
- Deduplicate only when it genuinely reduces complexity.
- Remove stale stubs/fallbacks/dead paths in touched files only after verifying
  nothing references them.
- Explicit beats clever. Match local project patterns and loaded rule packs.

## Workflow

1. Identify changed files and the task's intent; read surrounding code first.
2. Apply small behavior-preserving edits to the working tree.
3. Run lint/build/tests for edited files — a cleanup that breaks the build is
   worse than slop.
4. **Report the diff summary**: what was removed/simplified and why, per file.

## Boundaries

- Working-tree edits only: never commit, push, or amend.
- If a simplification would change behavior, don't do it — list it as a
  suggestion instead.
- If `review` already produced findings on these changes, apply only the
  clear-cut ones; contested findings go back to the human.
