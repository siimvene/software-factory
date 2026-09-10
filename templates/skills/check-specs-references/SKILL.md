---
name: check-specs-references
description: Use this skill when the user wants to check whether the git repositories referenced in a specs repo's `.tech-refs.md` files are checked out locally, e.g. "check if the repos referenced in the specs are checked out", "verify specs dependencies", "which repos does team-specs reference and are they cloned". Requires the name of a specs folder that is a sibling of the current project's root.
version: 1.0.0
---
<!-- Ported from the group's spec-repos plugin, 2026-09-10, anonymised. Logic unchanged except where 17-onboarding.md section 5 is cited. -->

# Check if specs reference checked-out repos

Scan all `.tech-refs.md` files in a **specs repository** (a sibling folder of the current project) to find which git repositories are referenced via the `{git repos path}` placeholder, then check whether each one is present on disk.

See `../README-specs.md` for the specs-repo convention this relies on (one specs repo, subdomain folders, paired `<slug>.md` plus `<slug>.tech-refs.md` files).

**Argument**: The name of the specs folder (e.g. `team-specs`). This folder must be a sibling of the current project's root directory.

## Steps

1. **Resolve paths**:
   - The current project's root is the directory containing the project's `CLAUDE.md` (or the current working directory if none is found above it).
   - `{git repos path}` = the parent of the current project's root (the shared parent of both this project and the specs folder).
   - Specs folder = `{git repos path}/{argument}`.

   Example:
   - project root = `/code/<org>/some-project`, argument = `team-specs`
   - `{git repos path}` = `/code/<org>`
   - specs folder = `/code/<org>/team-specs`

2. **Find referenced repos**: Run the cross-platform helper script if Node.js is available, passing the specs folder name and the resolved project root:
   ```
   node scripts/check-tech-refs-repos.js <specs-folder-name> <project-root>
   ```
   The script scans all `*.tech-refs.md` files inside the specs folder for the pattern `\{git repos path\}[\/\\]([^\s\`\)\/\\]+)` and collects the unique captured repository folder names.

3. **Check presence**: For each unique repository name, check whether a directory with that name exists directly inside `{git repos path}`.

4. **Report**: Print:
   - The resolved `{git repos path}` value
   - The specs folder being scanned
   - A list of every referenced repo with a check mark (directory exists) or a cross (directory missing)
   - A summary: all present, or a note that missing repos should be cloned into `{git repos path}`
