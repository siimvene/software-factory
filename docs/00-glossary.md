# Glossary

Terms are defined once, here, in the sense this design uses them.

**Software factory.** A delivery line that runs lights-out: humans specify outcomes and
constraints, machines build, inspect and ship, and people inspect output rather than process.
"Dark" describes where the humans are not, not the absence of supervision on risk.

**Flywheel.** The property that makes a software factory accelerate rather than merely automate:
the substrates (verification net, knowledge plane, gates, pattern library) compound with every
feature shipped, so turn N+1 is cheaper and safer than turn N.

**Turn.** One pass of the loop for one unit of intent: a ticket in, a merged and released
change out, with the two write-backs done.

**The loop.** SPEC → BUILD → VERIFY → SHIP → LEARN. See [02-loop](02-loop.md).

**Write-back.** The LEARN edge. Two of them: merged changes regenerate the current-state
specs; matured working memory promotes into the team store. Both are human-reviewed PRs.

**Knowledge plane.** Everything an agent reads that is not the code: the repo's agent
instructions, the team-context repo (specs, decision records, memory store, rubric), the
operating contract. See [04-knowledge-plane](04-knowledge-plane.md).

**Team-context repo.** A repository per team holding current-state specs, cross-repo decision
records and the durable memory store, bound read-only into each code repo.

**Spec (current-state).** A generated description of what the code does today, per feature,
in business language plus a technical-references sibling. Derived, never hand-edited.

**Ticket.** The delta: what should change, with numbered observable examples. The only
hand-written intent artifact. See [templates/ticket.md](../templates/ticket.md).

**Program design note.** The BUILD-stage artifact between the architecture and the code for a
sized ticket: modules and lanes, types, signatures and call paths, shape decisions with the
rejected option, slices in landing order, and the tests that must be red on the merge base.
Written by the head, reviewed before the first brief, read by the panel as a pack. See
[templates/program-design.md](../templates/program-design.md).

**Decision record (ADR).** A dated record of a live architectural decision with its
rejected alternatives and consequences. Repo-level ones sit in the code repo, cross-repo ones
in the team-context repo.

**Memory (memspec).** Structured, typed, dated claims (fact, decision, procedure) with
check-by dates and code anchors. Local scratch is disposable; the team store is durable and
reached only by promote PR.

**Sensor stack.** The four mechanical, model-free layers that run around a change:
orientation map (pre-write), YAGNI ladder (during write), quality ratchets (post-write),
architecture diff (post-write). See [05-sensor-stack](05-sensor-stack.md).

**Ratchet.** A gate whose baseline records the debt present on adoption day and which fails
on new debt or on baselined debt that got worse. It never loosens by itself; loosening is a
person's reviewed commit.

**Gate.** A check that fails, names file and line, says what fixes it, and refuses to say how
to make the baseline accept it. A rule in a document is a suggestion; a gate is enforcement.

**Consort gate.** The inferential VERIFY step: a cross-vendor, non-inheriting-context review
of the cumulative diff, plus a blind security side-pass and a scanner tier, before any push.
See [06-verify-gate](06-verify-gate.md).

**Three axes.** What makes a review count as a consort pass: cross-vendor (a different
vendor's model), non-inheriting (the reviewer never saw the author's session), verification
before action (findings are hypotheses to check against code, not a work queue).

**Head and hands.** A delegation shape: the head (an expensive model) selects, designs,
reviews, directs remediation and runs the gate; the hands (a cheaper model or a second vendor,
fresh process per call) implement. The head verifies everything itself.

**PM hat / dev hat / owner.** The three human roles a turn touches. PM: intake and
acceptance of behaviour. Dev: operates the agents, reads evidence, owns exceptions. Owner (code
owner, release owner): merges and presses release. A solo operator wears all three and records
every shortcut.

**Provenance trailer.** Commit metadata naming the agent and session that authored a change.
Humans approve and merge; they do not author. A trailer-less commit is rejected.

**Verification net.** The tests, coverage ratchet, mutation kill rate, characterization suite
and self-provisioning test infrastructure that make lights-out changes safe on a given core.
Coverage says a line ran; the kill rate says a test would notice it changing; the net needs both.
On a legacy core, building it is turn 1.

**Fail-on-base check.** The gate that runs every new or changed test at the merge base with the
branch's tests applied and requires it to fail there and pass on the branch. Declared
characterization and refactor tests are the only tests allowed to pass on both. The mechanical
form of "tests first, red on the unfixed code".

**Characterization test.** A test that locks current behaviour, bugs included, so that a
refactor or port can be judged against it. A refactor net, not a correctness proof.

**Oracle / parity replay.** A mature system used as an executable specification: replay the
same input against the oracle and the new implementation and diff the outputs (money paths
cent-exact). Catches "works but wrong", which unit tests and review cannot.

**Blast-radius ladder.** The rungs a change climbs, each mechanical: sandbox, verification
net, parity replay, adversarial review loop, contract and architecture gate, acceptance on
evidence, staged release with auto-revert. See [11-scaling](11-scaling.md).

**Money-critical / transaction tier.** Code where a wrong change moves wrong money. Requires
named-human outcome sign-off, always. Tiered per class, not per module.

**Dogfood report.** The per-cycle record of wall-clock per stage, tokens per agent, what the
gate caught, and every skipped or shortcut step. The input to any organisational proposal.

**Evidence class.** measured / designed / proposed / field. See [WRITING.md](../WRITING.md).
