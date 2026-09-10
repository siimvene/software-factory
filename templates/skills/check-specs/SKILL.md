---
name: check-specs
description: Use this skill when the user wants to validate a specs repository before opening the specs PR, e.g. "check the specs", "validate the spec folders", "are all the spec pairs complete and the cited paths real", "lint the specs repo". Runs the three checks over every feature folder: both files present, every cited path exists, no code identifiers in the business spec.
version: 1.0.0
---
<!-- Ported from the group's spec-repos plugin, 2026-09-10, anonymised. Logic unchanged except where 17-onboarding.md section 5 is cited. -->

# Check a specs repository

Validate a specs repository over every feature folder. This is the checker the reference implementation lost: in that project the check lived in a scratch directory that was gone by the next cycle, and the three checks had to be done by hand (17-onboarding.md section 5, the check step). Keeping it as a skill in the team repo is what makes it survive the session that wrote it.

The script `scripts/check-specs.py` runs three checks:

1. **both-files**: every feature entry in every folder has both `<slug>.md` (business-facing) and `<slug>.tech-refs.md` (technical paths).
2. **cited-path**: every path cited in a `.tech-refs.md` exists in the sibling checkout named by its heading. Headings (`## Project`) name the project; the cited path under each heading is relative to that project's checkout. `--root <dir>` gives the parent of the sibling checkouts (default `..`).
3. **code-identifier**: the business spec contains no code identifiers. Heuristic: it flags any backticked token that contains `/`, `.py`, `.ts`, `.java`, `::`, `()`, or is a CamelCase word with an internal capital.

## When to run it

- **Before the specs PR.** Run it over the spec folders you just generated (see `retrogenerate-specs`, the Check step) so the PR the owner reads for business truth is not carrying missing pairs, dead path citations, or jargon that leaked into the business spec.
- **Keep it in the team repo, not a scratch directory.** The reference implementation's checker was thrown away with its scratch directory and the checks reverted to manual. Commit this skill and its script into the team's specs repo so it survives the session and every later cycle can run the same three checks.

## Usage

```
python3 scripts/check-specs.py <specs-dir> [--root <parent-of-checkouts>]
python3 scripts/check-specs.py --help
```

- `<specs-dir>`: the specs repository (or a subdomain folder inside it) to check.
- `--root`: parent directory of the sibling code checkouts named by the `.tech-refs.md` headings. Defaults to `..`, the convention where the specs repo and the code repos are siblings.

## Output and exit codes

- One line per finding: `<check> <file>: <detail>`, where `<check>` is `both-files`, `cited-path`, or `code-identifier`.
- Exit `0`: clean, no output.
- Exit `1`: one or more findings printed.
- Exit `2`: usage error (bad or missing arguments).

Python 3 standard library only, no dependencies to install.
