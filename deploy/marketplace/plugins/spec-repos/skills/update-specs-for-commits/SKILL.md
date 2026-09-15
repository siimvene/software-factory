---
name: update-specs-for-commits
description: Use this skill when the user wants to keep a specs repo in sync with recently implemented work — e.g. "update the specs for this story", "a story was implemented, sync the specs", "keep specs in sync with these commits", "generate/update specs for what was just merged". Takes a specs repo plus one or more repo:commit pairs where a story was implemented, and either adds a new feature spec or updates an existing one.
version: 1.0.0
---

# Update specs for implemented commits

Given repos + commits where a story was implemented, keep the specs repo in sync: add a new feature spec pair if the commits introduced a new feature, or update the existing pair(s) if they modified one already documented.

See `../../references/spec-repos-concept.md` for the specs-repo convention this relies on (one specs repo, subdomain folders, paired `<slug>.md` + `<slug>.tech-refs.md` files per feature).

**Invocation**:
```
/update-specs-for-commits <specs-repo> <repo>:<commit-or-range> [<repo>:<commit-or-range> ...]
```
- `<specs-repo>` — name of the specs folder, a sibling of the current project's root (same convention as check-if-specs-references-checkedout)
- `<repo>:<commit-or-range>` — a repo name (sibling of the current project's root) and a commit SHA or range in that repo where the story was implemented; pass one pair per affected repo

## Steps

1. **Resolve paths**, same rule as `check-if-specs-references-checkedout`:
   - The current project's root is the directory containing `CLAUDE.md` (or cwd if none found above it).
   - `{git repos path}` = the parent of the current project's root.
   - Specs folder = `{git repos path}/<specs-repo>`.
   - Each `<repo>` in the argument list resolves to `{git repos path}/<repo>`.

2. **Gather the diff, per `<repo>:<commit-or-range>` pair**:
   - Run `git show --stat <commit-or-range>` (or `git diff <range> --stat`) inside `{git repos path}/<repo>` to get the list of changed files.
   - Run `git log` on the same commit(s) to capture the commit message(s) as story/intent context.

3. **Find which existing features are touched**: search every `*.tech-refs.md` file under the specs folder for bullet paths that overlap the changed files. A bullet overlaps if its path (prefixed by the repo name, matching the same `{git repos path}/<repo>/...` convention used in `.tech-refs.md`) is a prefix of, or shares a directory with, a changed file's path. Build a map of `feature spec file → matching changed files` per repo.

4. **Classify each changed area**:
   - **Overlap found → existing feature, modified**:
     - Update that feature's `<slug>.tech-refs.md`: add bullets for newly touched paths not already listed (with a one-line description of their new role), and remove bullets for paths that are clearly no longer relevant (e.g. deleted files, code that moved elsewhere).
     - If the diff changes user-facing behavior (new field, new role, new validation rule, changed flow), update the paired `<slug>.md` to describe the change in plain language — add/edit the relevant H2 section rather than rewriting the whole file.
     - Apply the same quality rules as `retrogenerate-specs` Mode 3: no jargon in `.md`; only real, verified paths in `.tech-refs.md`.
   - **No overlap → new feature**:
     - Derive a feature slug from the story/commit message (kebab-case, e.g. `create-edit-and-remove-a-show`).
     - Pick the target subdomain folder inside the specs repo. If it's not obvious from the commit message or from memory saved by `retrogenerate-specs prepare`, ask the user to confirm.
     - Write both `<slug>.md` and `<slug>.tech-refs.md` in that subdomain folder, following the exact same two-file format and quality rules as `retrogenerate-specs` Mode 3 — but source the content from the diff and commit message(s) plus any needed targeted exploration around the changed files, rather than a full project scan.

5. **Report**: list every spec file created vs. updated, and for each one, which changed files (repo + path) drove the decision.
