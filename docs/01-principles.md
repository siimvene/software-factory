# Principles

Ten rules the rest of the design is built on. Each one was paid for; the price is noted.

## 1. Gates, not instructions

A rule in a context file is a suggestion. It holds until the model is deep in a long chain of
steps and skips it. A gate fails, names the file and the line, says what fixes it, and, wired
into the agent's own loop, becomes the next thing the agent works on.

Every rule in this design is therefore written twice: as the rule, and as the check that
enforces it. Where no check exists yet, the rule is labelled advisory, and that label is a
backlog item.

Paid for: a "local only, no push" rule for the legacy core was written in the project's agent
instructions and then backed by a pre-push hook that rejects every push. The hook fired; the
sentence never had to. A ratchet baseline that the agent was told never to edit was protected
by a pre-tool guard; the guard refused the agent's own baseline re-cut and a PR body that
merely quoted the flag `[measured 2026-09-07]`.

## 2. Intent is not completion; execution is not verification

No completion claim without fresh evidence. Name the command that proves the claim, run it,
read the whole output, then claim. Red flags that force a re-check: "should" instead of "is",
reporting from memory, one summary covering several changes, time passed since the change.

Stated uncertainty demands a named check. "Might need to look at X" must name the command
that resolves it, or be retracted, or be promoted to a question.

Paid for: a coverage tool reported "verified in CI" for a change nobody had run locally; run
locally, the coverage library could not read the JVM's bytecode version and failed
`[measured 2026-09-04]`. The claim was intent dressed as completion.

## 3. Test the test

Before trusting any scan, filter or predicate over a large space, run it once on a case known
to be true and once on a case known to be false. If both return the same thing, the predicate
is blind. A scan that cannot fail is a confident wrong answer.

Paid for: the money-surface predicate on the legacy core self-tests 15 cases and withholds
every number if one misclassifies. The layering rules were validated on 10 cases (4 must
match, 6 must not) after the first draft reported 7 violations that were all legitimate
test-scope dependencies `[measured 2026-09-04]`.

The test suite is itself a predicate over the code, and the same rule applies to it. Coverage
is the known-true case: a line ran. Mutation is the known-false case: a planted change in that
line must turn a test red. A suite with green coverage and a low kill rate is blind in exactly
the way a scan that cannot fail is blind. Paid for on the reference implementation: coverage
green across the service layer, whole-module kill rate 30.3 % on 59 database-free modules
(5,394 of 17,783 mutants) and 39.9 % on 81 database-coupled modules (11,709 of 29,341), and
11.2 % on the largest billing module (235 of 2,095) `[measured 2026-09-15]`. Rule: report
mutation as killed over all mutants; killed over (killed plus survived) hides the uncovered ones
and read 100 % on a module 3.6 % of whose mutants were ever exercised. The gate this argues
for is in [05-sensor-stack](05-sensor-stack.md), the net.

The change has a known-false case of its own: the code before it. A test shipped with a change
must fail on the merge base and pass on the branch; one that passes on both proves something
that was already true. The loop's `red-before` row has been a hand step since cycle 1
`[measured 2026-09-07]`; its check is the fail-on-base gate in
[05-sensor-stack](05-sensor-stack.md) `[proposed]`.

## 4. Humans inspect output, not process

Every human touchpoint is a decision on evidence: an approved ticket, an accepted behaviour, a
pressed release. Reading a diff is what the gates and the cross-vendor reviewer do. When a
human is reading code to decide, a gate is missing.

Consequence: what gets presented to a human is a table of observed outcomes against numbered
examples, a gate report, and a diff against an oracle. Not a PR body written by the author
model.

## 5. Mechanical before inferential

Deterministic sensors have zero hallucination risk and near-zero cost per run. A model review
of code that a ratchet would have failed wastes the most expensive resource. So the mechanical
stack runs first and the cross-vendor reviewer sees only what survived it.

Paid for: the cross-vendor review is 52 to 58 % of the dev-hat wall-clock in the kvart cycles
`[measured 2026-09-07]`. Anything the ratchets can take off that reviewer's plate is minutes
saved per turn.

## 6. Cross-vendor, non-inheriting, verified

One model family shares its blind spots with itself. The review that counts is by a different
vendor's model that never saw the author's session, and its findings are hypotheses to check
against code before anyone acts on them. Disbelieve at least one rejected finding per panel.

Paid for: the authoring model found 0 of 10 defects a fresh reviewer found 4 of
`[measured 2026-08-19]`. On a streaming export, tests and lint were green and the cross-vendor
reviewer found a per-token ASGI send (32,018 sends for 2,000 rows) `[measured 2026-09-05]`. On a
money-path retirement, the author's own scoping had dropped a poller that nothing else replaced;
the cross-vendor reviewer caught it `[measured 2026-09-07]`.

## 7. Ratchets, not floors; baselines are people's decisions

A floor is negotiated once and forgotten. A ratchet records the debt present on adoption day
and fails on new debt or on baselined debt that got worse. It never loosens by itself.
Accepting worse numbers is a person's reviewed commit, and the gate refuses to tell the agent
how to do it.

Paid for: a function baselined at complexity 10 / 48 lines measured 15 / 100 on the main
branch. The first reading called it a bootstrap artifact; it was a real regression the ratchet
had caught `[measured 2026-09-06]`.

## 8. Adopt, do not rebuild

Before building a harness, check whether the organisation already ships one. The first
design for the legacy core built its own gate set, module map, spec template and memory
topology in parallel to a standard that already shipped all of them. Every generic mechanism
comes from the standard; only the system-specific pieces are built locally.

Paid for: one full design version discarded `[measured 2026-09-04]`.

## 9. Measure before agents dominate

Revert rate, defect escape rate and cost per merged feature must be baselined on human-written
code before agents author most PRs. Once they do, the comparison point is gone for good.

Paid for: not yet, which is the point. Field evidence says spend flattens only after per-outcome
metrics and governance exist `[field: Uber Engineering]`.

## 10. A constraint without an instrument is a vibe

Before any unattended run: name the target and its mechanical check, the constraints
(wall-clock, spend, surface allowlist), and one inspection command per constraint. If one
cannot be named, the run does not start.

Paid for: a head process delegated to a hands process with stdin inherited, the child hung on
"reading additional input", the head invented a benign story and ended its turn waiting.
2 h 08 m of a 3 h run were idle; the real cycle was 24 minutes `[measured 2026-09-05]`. The
fix was a wall-clock cap, `< /dev/null`, and the rule that empty output plus empty diff is a
failure signal, not a curiosity.
