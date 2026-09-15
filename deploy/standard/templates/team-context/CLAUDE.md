# [Team name] team context

[One sentence: what this team builds and for whom.]

## What we own

- [product or service]: [one line on what it does]
- [product or service]: [one line on what it does]

## Code repositories

[One bullet per repo, `org/repo` slug first, optional short note after. Write
`none` if the team owns no code repos. PM tooling reads this section to
discover your repos, so keep it current.]

- Piletilevi/[repo-one]
- Piletilevi/[repo-two]

## Where things live

- Current-state specs: `specs/` in this repo (generated, never hand-edited)
- Decisions: `docs/adr/` in this repo
- [test environment]: [URL]
- [dashboards / monitoring]: [URL]
- [design system, API docs, anything an agent would otherwise have to guess]

## Domain vocabulary

[Terms an outsider (or an agent) would get wrong. One line each.]

- [term]: [what it actually means here]
- [term]: [what it actually means here]

## Cross-repo rules

[Rules that hold across every repo the team owns. Repo-specific rules belong in
that repo's own CLAUDE.md, not here.]

- [rule]
- [rule]

<!--
Keep this file under ~150 lines and link outward instead of inlining.
Wherever the context-standard wiring is present (sandbox mount + repo imports),
this file loads into every agent session across all the team's repos: no file
the team writes has a bigger blast radius per line. Review changes accordingly.
A filled-in example:
https://github.com/Piletilevi/plg-development-standards/blob/main/templates/team-context/EXAMPLE-CLAUDE.md
-->
