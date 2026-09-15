# Team-context repo template

Starting point for a `Piletilevi/<team>-team-context` repo: the one shared
repository holding what every AI agent should know about your team's world.
The full walkthrough lives in the wiki ("Team Context Repo: Setup Guide for
Engineering Teams" under the AI Developer Guide); the normative contract is
[context-standard STANDARD.md §8](../../context-standard/STANDARD.md).

## Fastest path

1. Create the private repo `Piletilevi/<team>-team-context`.
2. Copy `CLAUDE.md` and `CODEOWNERS` from this folder into it. Grab
   `EXAMPLE-CLAUDE.md` too while you work (delete it before you merge).
3. Fill in the `CLAUDE.md` brackets with the example beside you. Better still:
   open Claude Code in the fresh repo and say *"Read CLAUDE.md and
   EXAMPLE-CLAUDE.md, then interview me and fill in the template for my team."*
   You edit the draft instead of writing from scratch.
4. Fill the `CODEOWNERS` placeholder with your team's GitHub team or the
   lead's handle (owners need write access to this repo). Only then enable
   branch protection requiring code-owner review on the default branch;
   protection with an unresolved placeholder makes the gated paths unmergeable.
5. Bootstrap `specs/` with the `retrogenerate-specs` skill (from the
   `spec-repos` plugin in the `plg-skills` marketplace, sourced from
   `Piletilevi/plg-ai-plugins`; install it first with the `/plugin` command).
   The PM reviews the output for business truth; the code owner merges.
   From then on, every PR that changes behavior ships a sister spec PR via
   the `update-specs-for-commits` skill from the same plugin.
6. Wire each code repo to the new team layer. Run from a checkout of this
   repo (`plg-development-standards`), against a code repo that has already
   adopted the context standard:
   `./context-standard/adopt.sh --set-team Piletilevi/<team>-team-context <repo>`
   Then check the code repo's `.memspec.yaml`: adoption seeds it with a
   `{{TEAM_CONTEXT}}` placeholder, and it must point at the new team repo.

## What the files are

- `CLAUDE.md`: the bracketed template for the team's agent front door.
- `EXAMPLE-CLAUDE.md`: the same file filled in for a fictional bookstore team,
  so you can see what good looks like. Copy the template, not the example.
- `CODEOWNERS`: routes `specs/` and `.memspec/` to the team lead/devs, which is
  what turns the write gates from etiquette into mechanics.

`docs/`, `rules/`, and `.memspec/` need no templates: `docs/` is free-form,
`rules/` is optional review rubrics, and the memory engine lays out `.memspec/`
itself on first promote.
