# 0017. Mechanical changes ship as a recipe: the recipe is reviewed, the diff is checked to be its output

- **Status:** proposed
- **Date:** 2026-10-15
- **Deciders:** the operator, the principal session that proposed it

## Context

Some changes are the same edit at many sites: a rename across modules, a migration from a
deprecated API to its replacement, a dependency's major version with renamed coordinates or
types, a logging or error-handling call reshaped everywhere. The legacy core met one of these
shapes: a library renamed its module artifacts across a major version while leaving the old
coordinates published, and pinning the old names produced a split-brain classpath that compiled
against one version and ran against the other `[measured 2026-09-04]`
([09-legacy-adoption](../docs/09-legacy-adoption.md)).

Today such a change goes through the loop like any other. The builder edits each site by hand,
so cost and wall-clock scale with the number of sites, and every site is a chance for a
slightly different edit. The sizing rule ([adr/0010](0010-program-design-before-the-plan.md))
counts modules, so a rename touching 6 modules is a one-note ticket and gets a program design
note for a change with no design in it. The panel then reads an N-file diff in which the only
interesting hunk is the one that differs from the rest, and nothing checks that every site was
reached. A wide diff also conflicts with most other open PRs, which is the stale-base problem
of [adr/0013](0013-merge-serialization-substrate-for-delegated-merge.md) at its worst.

The usual answer outside this design is a codemod: a deterministic transformation the engineer
writes once, reviews once, and runs everywhere. Large monorepos have run repository-wide changes
this way for years. Two current sources make the same argument for agents. A vendor one-pager
claims 14 to 26 times lower cost when an agent routes refactoring to a compiler-based tool
instead of editing by hand; it is a marketing sheet on one 50k-line C++ codebase with no task
list, N or variance, so it counts as direction, not measurement. Anthropic's code-modernization
plugin routes the mechanical deltas of a version uplift to OpenRewrite's dry run rather than to
the model `[field: codemods]`.

Nothing in this design names a codemod: a search for OpenRewrite, codemod and Refaster over the
repository finds nothing. No mechanical change has been measured on kvart.

Assumptions, stated: each stack in scope has an AST-level codemod tool that is deterministic for
a pinned version (OpenRewrite for Java with Gradle or Maven, Refaster or Error Prone for Java
patterns, LibCST for Python, ts-morph or jscodeshift for TypeScript; Vue single-file components
need an SFC-aware tool, since jscodeshift alone does not parse them); the builder can write a
recipe and its tests in that tool as well as it writes code.

## Decision

We will give mechanical changes their own ticket class, in which the builder writes a recipe,
the panel reviews the recipe, and a script proves the diff is exactly the recipe's output.

1. **The class.** A ticket is `mechanical` when the change is fully expressible as a
   deterministic transformation and is meant to preserve behaviour, or to swap one API for one
   documented as equivalent. Signal: the same edit at 5 or more sites, or across 3 or more
   modules. The ticket names the class, the transformation in one sentence, and the residual
   query (step 4b); a person approves it like any ticket (adr/0005). A behaviour change is never
   mechanical, whatever its width.
2. **The recipe.** The builder writes the transformation in the stack's codemod tool, with
   before-and-after tests in that tool's test harness, under `codemods/<ticket key>/`, with the
   tool version pinned. A scripted text substitution counts as a recipe only for non-code text
   (configuration, docs, translation catalogues); code goes through an AST tool.
3. **The PR shape.** Three commits, in order: the recipe and its tests, touching nothing outside
   `codemods/<ticket key>/`, on the current base; the recipe's output and nothing else, its
   message naming the recipe path; and, only if needed, the hand edits the recipe cannot express.
   The recipe never rewrites `codemods/`, whose test fixtures hold the old form on purpose. The
   formatter runs as part of the recipe step, pinned, so its output is inside commit 2.
4. **The mechanical checks,** written to a receipt per tree like the browser and static-analysis
   gates:
   - (a) **Reproduce.** Check the shape first: commit 1's parent is the merge base with the
     current target branch, and commit 1 changes only `codemods/<ticket key>/`. Then re-run the
     pinned recipe on commit 1 itself, commit 2's actual parent, never on a commit a message
     names. The resulting tree is byte-identical to commit 2's. A hand edit hidden in commit 2
     fails here, and one hidden in commit 1 outside `codemods/` fails the shape check.
   - (b) **Residual.** The ticket's query for the old form (an AST pattern, or a search over
     code and non-code files) returns 0 outside `codemods/` and declared exemptions, each with a
     reason. String
     references, reflection, serialisation names, SQL, configuration and translation keys are
     where a rename survives a compiler; the residual query searches them.
   - (c) **Build and the full suite.** Not impact-selected: a wide diff selects nearly
     everything, and a full run removes the selection question.
   - (d) **Fail-on-base exemption.** Commit 2 adds no behaviour, so it adds no red-first test;
     the gate report declares the exemption `mechanical` (adr/0010). The recipe's own tests in
     commit 1 run in the codemod tool's harness, not the product suite, and are declared
     `mechanical-recipe`. Commit 3 gets the normal check.
5. **The review.** The panel reviews commits 1 and 3 in full. For commit 2 it receives the
   diffstat and a sample chosen by script: the largest hunk, one hunk per module, and every hunk
   in a money, tenant or identity file. The recipe review asks: does the match reach too far
   (false positives), not far enough (the residual), and does the transformation preserve
   behaviour at the edges (overloads, reflection, serialised names, wire contracts). A money
   path touched by commit 2 selects its path tests as usual (adr/0012).
6. **Rebase by re-running.** When the base moves, commit 1 is rebased (it touches only
   `codemods/`, so it does not conflict), commit 2 is dropped and regenerated by the recipe, and
   commit 3 is re-applied. Then every check runs again on the new tree, (a) to (d): code merged in
   the meantime can add a site in the old form or break the build, and a reproduce check alone
   would not see either. A conflict in commit 2 is never resolved by hand. This makes the class
   cheap under adr/0013's merge on the current base.
7. **Ratchet exemption, declared and narrow.** Only changed-line coverage is exempted, and only
   for commit 2's lines: they are the recipe's and the full suite is the check. It is computed
   over commit 3 alone (base set to commit 2), so hand edits are held to the normal rule. Every
   other ratchet (escapes, conventions, layering, complexity) blocks on the whole diff as usual,
   so a recipe that writes `# type: ignore` at 200 sites fails like a person who did. The
   exemption is written in the ticket, so the person approving the ticket approves it (adr/0004:
   a baseline is a person's decision).

Scope: repositories whose stack has a codemod tool in the list above, or one the adopter adds.
The class is opt-in per ticket. When the recipe covers less than the whole change and commit 3
grows past a few hand edits, the ticket is reclassified and goes through the normal loop.

## Consequences

- **Positive:** the reviewed artifact is a recipe of tens of lines instead of a diff of hundreds;
  "every site was reached" is a query with a count, not a reviewer's impression; a hand edit
  cannot hide in generated code; a moved base costs a re-run instead of a conflict resolution;
  the builder's cost scales with the rule, not with the number of call sites, if the field
  direction holds on our stacks.
- **Cost:** a codemod tool per stack, its pin and its learning curve for the builder; a recipe
  for a small change can cost more than the edits it replaces, which is why the class has a
  threshold; the reproduce check needs the tool in CI or in the pre-push hook; the Vue SFC case
  has no tool chosen yet.
- **Follow-ups:** a `mechanical-check` script (reproduce, residual, exemptions, receipt), with
  planted cases for a hand edit in commit 2 and a missed site (owner: the operator); the class
  row in the sizing table of [02-loop](../docs/02-loop.md) and the ticket template field (owner:
  the operator, when accepted); the first trial on kvart: a real rename in the Python backend done
  twice, once by hand and once by a LibCST recipe, measuring tokens, wall-clock, review time and
  sites missed (owner: the operator); the legacy core's next library major as the OpenRewrite
  trial (owner: the group's platform role); the review tool: the commit-2 sampling as a pack
  (owner: the tool's maintainer).

## Alternatives considered

- **The status quo, the builder edits every site:** cost scales with sites, the panel reads a
  diff where the defect is the one odd hunk, and nothing checks completeness. Rejected for
  changes over the threshold; kept below it.
- **Hand edits plus a residual search:** checks completeness, but the panel still reads every
  hunk and cannot tell a deliberate deviation from a slip. Rejected; the reproduce check is what
  makes a sampled review of commit 2 safe.
- **The editor's rename refactoring through a language server:** deterministic, but it leaves no
  artifact to review or re-run, and covers renames only. Allowed as a tool inside a scripted
  recipe, not as the recipe.
- **Regular-expression substitution for code:** blind to syntax and scope, so it matches strings,
  comments and shadowed names. Allowed for non-code text only.
- **A vendor refactoring service:** the one sampled supports C++ only and publishes no method.
  Rejected for now; the decision does not depend on a vendor.

## Evidence

- [docs/09-legacy-adoption.md](../docs/09-legacy-adoption.md): the renamed artifacts and the
  split-brain classpath `[measured 2026-09-04]`.
- [evidence/kvart-stale-green-merges-2026-09-29.md](../evidence/kvart-stale-green-merges-2026-09-29.md):
  why a wide diff on a moving base is expensive.
- [evidence/field-evidence.md](../evidence/field-evidence.md) §9: the three field sources and
  their caveats `[field: codemods]`. Direction only; no mechanical change has been measured on
  kvart.
