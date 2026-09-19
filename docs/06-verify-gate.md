# Verify gate

The inferential half of VERIFY: what runs before any push, what counts as a pass, and how to
tell a clean verdict from a review that never happened.

## The gate, in one list

Before any push containing code changes:

1. **Scanner tier.** Secret scan on the diff, dependency vulnerability scan, static analysis
   where a server exists. Every skipped or failed scanner line is repeated in the report. A
   reachable scanner critical (live credential, critical CVE in a dependency the diff adds) gates
   like a CRITICAL model finding.
2. **Cross-vendor review** of the cumulative diff by a non-Anthropic reviewer that never saw the
   author's session. Findings classified CRITICAL / SERIOUS / MINOR.
3. **Blind security side-pass**: a security-only reviewer on the same diff, non-inheriting. Same
   vendor as the author is allowed here because it is additive; it never satisfies axis (a).
4. **Surface QA pass** on every UI surface the diff touches, as the right persona, on the
   platform's real runtime: a browser for the web client, a simulator or emulator through the
   platform harness for a native client. Rendering, console, interactions and locales; findings
   with screenshots. Two rules that the 2026-09-17 kvart-app incident added (below, "Native
   client QA"): a platform the diff touches with no runtime available is a **FAILED** line in the
   gate report, never a skipped one; and where the ticket names a prototype view for a surface,
   the surface's screenshot is placed next to that view and compared, and a mismatch is a
   **SERIOUS** finding with the same weight as a cross-vendor HIGH. Prototype conformance is a
   verifier's job, above the builder's tier, never the builder's own check.
   The web pass is a receipt-checked pre-push gate (see below), scoped to the routes the diff
   can reach.
5. **Adjudication.** Spot-verify every CRITICAL and SERIOUS claim against code. Fix those before
   push. Log MINOR with a disposition. Disbelieve at least one rejected finding per panel.

Exempt: docs-only and memory-only commits. A docs commit that encodes a security rule or a data
model decision is reviewed anyway.

The net runs before this list, on the Stop hook and the pre-push receipt: ratchets, changed-line
coverage and, proposed, the mutation kill rate on the touched modules
([05-sensor-stack](05-sensor-stack.md) layer 3). A reviewer reading a diff whose tests kill
nothing is reviewing the wrong artefact. The fail-on-base check sits in the same place: every
new or changed test red on the merge base and green on the branch, exemptions declared, so the
reviewer is not the party that discovers a test proves nothing (the trial's MINOR, below).

## Design review before the build (proposed)

For a sized ticket ([02-loop](02-loop.md), the sizing rule) the program design note is reviewed
before the first brief: one cross-vendor leg on the note for a one-note ticket, the panel and the
owner for a full one. The note is a page, so the leg returns in minutes, and it is the cheapest
review in the loop because nothing has been built yet. The reviewer is asked the adversarial
questions of the operating contract §4 against the note (what fails, which edge case breaks it,
can state be left inconsistent, which assumption might be wrong) plus two of its own: can every
numbered example pass while this design is still wrong, and does each slice boundary leave the
branch coherent. It flags and never edits; findings are dispositioned into the note before any
brief is written. The class it moves earlier is cycle 2's MEDIUM below: a planning document
keyed on a retired flag, found in the diff stage `[measured 2026-09-07]`. Not measured yet on
any cycle; the first sized ticket after this version is where it gets a number.

## Receipt-checked pre-push gates

Two of these checks are too slow to run on the Stop hook but must run before the push. Each runs
once, writes a receipt keyed by the git tree id, and the pre-push hook checks the receipt for the
pushed commit's tree.

**Browser QA.** The browser pass now runs before the PR, not after the merge `[measured 2026-09-09]`.
Scope is derived from the specs' own routes and the API routers' own paths (`scripts/ci/e2e-scope.py`,
48 unit tests), so a diff pulls in only the Playwright specs it can affect. `scripts/e2e-gate.sh`
runs those specs through the existing harness and writes one receipt per git tree, and its
`--check` mode is what the pre-push hook calls. The hook refuses any pushed ref whose diff reaches
the browser without a receipt for that commit's tree. A scoped run is 23 s; the FULL run is 93 to
103 s over 27 specs and 42 tests. The receipt is bound to the exact tree, so any later commit or
baseline tighten voids it. The gate refuses to run while the app or API dev port is served by
another checkout and never attaches to a foreign stack (`E2E_GATE=1` disables the server-reuse that
would let it bind to whatever is already listening). One finding on this gate was acknowledged, not
fixed: the receipt is a local discipline file, never an authorisation token.

**Browser QA runtime.** The exploratory pass (step 4) is driven through the Playwright command-line
tool, one shell command per browser action, headless, one named session per persona
([adr/0008](../adr/0008-browser-qa-drives-a-cli-not-a-protocol-server.md)) `[designed 2026-09-10]`.
Login happens once per persona and the storage state is saved and restored, never logged in twice.
Each surface leaves a page tree, a console extract, a network extract and a screenshot on disk;
each exercised interaction is wrapped in a recording and a trace, and the recorded code travels with
the codify candidate in the report. The agent's context carries a few lines per action; the evidence
is read from disk when a finding needs it. Until 2026-09-10 the pass ran either through a headed
browser extension or through a script the agent wrote for the occasion, and the skill that describes
it was gitignored, so a station worktree could not run it at all. Check: the skill is tracked, and
the pass refuses to start when the runtime is missing instead of writing a script. Shakedown against
the running kvart stack `[measured 2026-09-10]`: persona login through the dev-login redirect chain,
state saved after the callback restores a logged-in session in a fresh browser, console and network
extracts as text, recording and trace per surface, teardown leaves no process.

**Native client QA.** The gate list above was written for a web client, and a native client
walked through it without step 4 for a whole release train `[measured 2026-09-17]`. The kvart
mobile overhaul (seven stacked PRs, four Suhtlus stories) passed scanners, cross-vendor review by
two vendors, a blind security pass, a three-lens verify panel and every ratchet, and the owner
still opened the app to the old notice-board screen under a new hub card, a colour monogram
misused for a role slot and a help screen whose human routes scrolled away under the chat. Every
gate had read a diff; no gate had looked at a screen. The clickable prototype was attached to each
ticket as the design input; no PR carried a single screenshot as the build's output; the device
harness that shoots one launch screenshot as smoke evidence existed and was never a gate. Two
causes, both of process: a story's acceptance criterion read "Teadetetahvel opens the announcement
list", which the old screen satisfied, so the destination screens behind the new cards were never
anyone's story; and the gate report's browser-QA row had nothing to say for a native client, so it
said nothing. The rules: a UI ticket names the prototype view per screen (14-pm-surface), every
route a card or row opens has a named view in some Ready ticket, the native harness shoots the
named routes into a screenshot directory the PR links, and the verifier compares each shot to its
view. The receipt shape is the same as the browser gate's once the harness can be scoped by route;
until then the screenshots are attached evidence and a PR without them for a UI story is not
ready for review.

**Static analysis.** The same shape wraps a local static-analysis scan `[designed 2026-09-09]`.
`scripts/sonar-gate.sh` runs a SonarQube scan scoped to the changed sources, computes the verdict
repo-side (CI has no Sonar server), and binds its receipt to the git tree plus the project set; the
same pre-push hook checks it next to the browser receipt. Limitation, already measured: in a worktree
without the Sonar properties file the scanner tier silently degrades to dependency scanning only, so
the gate report must say SKIPPED, not clean.

Why a receipt and not a CI job: until 2026-09-09 the browser pass ran only after the merge, as the
pre-deploy gate, so a browser regression could land on the default branch and be found only before
deploy; a receipt is what makes the pre-push hook able to refuse an unproven diff. The
rejected alternative is a CI end-to-end job on its own: it runs after the push, so the PR arrives
unproven. That job stays as the follow-up, not the gate.

## Spec-conformance finding (designed 2026-09-10, not yet measured)

Item 2's cross-vendor review checks the diff against itself: correctness, security, baselines. It
does not check the diff against what was asked for. The original work-loop design named this gap
directly: "intended-vs-derived reconciliation... the highest-value mechanical signal"
`[designed 2026-07-21]`, and no cycle since has run it. This is not the same mechanism as ADR
0007's spec-check skill, which regenerates current-state specs from merged code after the fact;
this one compares the diff, at review time, against the ticket or spec-delta that motivated it:
intent versus output, not output versus itself.

What the reviewer actually has in front of it was checked rather than assumed
`[measured 2026-09-10]`: the reviewer instruction asks for correctness, security and edge cases
over the diff plus the injected rule packs; the tool's own three packs carry no spec rule; the
spec lives in the team-context repository, which the code checkout does not contain; and one
leg reads only the diff payload. So a linked spec delta is not already in the reviewer's
context, and the check cannot be one line in a pack on its own. The plumbing is small but real:
the feature's spec, the ticket's numbered examples and the escalation decisions taken so far
travel to every leg as one more injected pack, the same mechanism the rule packs already use.
On a sized ticket the program design note travels with them
([templates/program-design.md](../templates/program-design.md)): drift from an agreed shape
decision, a signature or the slice order is the same `spec-drift` class citing the note's
section, and intended drift takes REFINE-SPEC into the note `[proposed, adr/0010]`.
The rule itself is then one paragraph. In cycle 4 the repo-reading leg raised the
management-company scope question from the code alone, the principal dismissed it "by the spec"
and escalated it, and the thread was posted at 12:53Z, after all three panels had finished; with
the spec in front of it the finding would have cited the section `[measured 2026-09-09]`.

Proposed rule-pack line, added to item 2:

> Cross-check this diff against the injected spec and the ticket's numbered examples. Report
> every addition, omission or behavioural divergence, in either direction, as a `spec-drift`
> finding citing the spec section or the example number. Default severity NOTE unless the
> divergence breaks a numbered example or lands on a money, tenant or identity path, in which
> case classify it by the normal CRITICAL / SERIOUS / MINOR rule.

Three constraints before this earns a `[measured]` tag, each already paid for elsewhere in this
design and reused here rather than relearned:

- **Severity default is NOTE, not a gate.** Mid-build spec deviation is the normal shape of
  discovery, not a defect: one dev-hat cycle ran six such deviations as live decisions with
  defaults and deadlines, all legitimate. Auto-blocking on divergence reproduces the review-load
  failure this whole gate design exists to avoid (principle 4: humans inspect output, not
  process). A `spec-drift` finding routes to the same escalation channel a human decision already
  uses; it does not fail the gate by itself.
- **Flag, never fix (principle 4; adr 0005, adr 0006).** The reviewer proposes a divergence; it
  does not edit the spec-delta to match the code it just reviewed. The silent-mutation failure
  that moved merge authority off the loop (adr 0006) recurs one layer up the moment a reviewer is
  allowed to resolve its own finding. The adjudicator, not the reviewer, gives intended drift the
  disposition REFINE-SPEC: it is written into the sister spec delta, and into the escalation
  thread when it is a product call, and the finding closes when the delta records it. Cycle 4's
  five refinements, written into the delta by hand after ship, become gate output.
- **Test the test before it ships as a standing rule (principle 3).** No data yet on whether any
  reviewer leg reliably tells real drift from noise. Recall on this panel is backend-dependent by
  a wide margin on ordinary findings (4/5 vs 2/5 vs 0/5 on identical known defects
  `[measured 2026-09-07]`); run the proposed line once against a diff with deliberately injected
  drift and once against a clean diff before it becomes a standing rule-pack entry, not after.
  If more than half of its findings on the first live cycle are dismissed, it is demoted to
  advisory and reworked.

Prerequisite this depends on and does not yet universally have: a spec delta to diff against.
Cycles 4 and 5 both shipped with the delta still open `[measured 2026-09-10]`, so the delta PR
is opened at gate time (a stub is enough) and becomes a receipt-checked pre-push gate in the
same shape as the browser pass: a behaviour-changing diff without a delta receipt for its tree
does not push. Where story creation produced only a ticket description rather than a committed
spec, the reviewer would be diffing the code against two sentences, a weaker and noisier signal
than the ADR 0007 sister-spec mechanism this complements and does not substitute for. The
decision record is [adr/0009](../adr/0009-the-spec-is-a-gate-input.md).

## The three axes

A review counts as a consort pass only if all three hold `[measured 2026-08-19]`:

- **(a) Cross-vendor.** A different vendor's model family, never a different model from the
  same vendor. Two families do not share blind spots: in one four-tool study, 93.4 % of issues
  were caught by exactly one tool `[field: consort README]`.
- **(b) Non-inheriting context.** The reviewer must not have the authoring session's context.
  Measured: the authoring model found 0 of 10 findings a fresh reviewer found 4 of. Same model,
  different context, different result.
- **(c) Verification before action.** Consort output is a hypothesis set, not a work queue.
  Volume is not confidence: the higher-volume vendor's HIGH findings are unverified until
  adjudicated.

The side-pass is in addition to the code review, not instead of it. Cross-repo mirrors inherit a
review only when the PR names the reviewed source diff and the mirror is mechanical; anything
carrying its own logic is new code.

## No re-run loop

Once a review has covered a diff, applying that review's own CRITICAL and SERIOUS fixes does not
trigger a fresh mandatory pass: the fixes are the response to the review, not new unreviewed
work. A re-review is optional for large reworks. Genuinely new code that no reviewer has seen
still needs its first run. Cycle 2 restored a poller the review said to keep; that is previously
reviewed code returning unchanged, not a re-run trigger `[measured 2026-09-07]`.

## Two backends, either satisfies the axis, hard-fail if both are down

Two cross-vendor backends exist: one OpenAI reviewer via its CLI runtime, one Google reviewer via
a cloud model API. Either satisfies axis (a). If every cross-vendor backend is unreachable
(billing, rate limit, expired credentials, API change) the gate FAILS. It never degrades to a
same-vendor review. Try the other backend; if both are down, say so and stop; do not push.

Transport matters as much as vendor. A CLI transport run in the working directory reads the
repo and does the repo-wide sweeps a rule pack asks for. A diff-only API transport sees the diff
payload plus the rule packs, fine for reviewing a diff, useless for "now go check every caller".
Measured A/B on the same 34-file diff: the diff-only transport returned in 86 s with one CRITICAL
that was a verified false positive; the repo-reading transport took 5 min 09 s and returned two
real defects that both needed repo access to see `[measured 2026-09-04]`. Wall-clock tells the
transports apart.

## Prove the reviewer ran

A zero-finding result and a failed review are easy to confuse, and the gate wrapper itself
emitted the former for the latter twice in one session before it was fixed `[measured 2026-09-04]`.
Two cheap checks, every time:

- **Reachability.** A probe call that must return a fixed token (`CODEX_ALIVE`). Proves
  reachability, not budget: a trivial call can succeed while a real one trips a spend cap.
- **Wall-clock.** A review of a multi-hundred-line diff that returns in seconds did not happen.
  Reference points: 7 min 06 s for a 48-line diff, 9 min 48 s for 1,383 lines, 20 min 19 s for a
  25k-line vendoring `[measured 2026-09-07]`.

The same logic applies to any agent reporting that a gate ran: a field report from a 200-engineer
shop describes a review agent that once posted "all done" without submitting the review after a
runtime update, and the fix was a hook that verifies the review was actually posted
`[field: Pipedrive]`. Do not trust the agent's self-report that a gate ran.

## Hands process discipline

When the reviewer or implementer is a child process: always `< /dev/null` or a payload on
stdin (an inherited open stdin hangs the child on "reading additional input"), always a
wall-clock cap, and never end a turn waiting on it. Empty output plus empty diff is a hang until
a named check (`ps` state, a growing log) says otherwise `[measured 2026-09-05]`.

## What the gate caught, with the class of thing tests missed

| Turn | Finding | Class | Why tests and lint passed |
|---|---|---|---|
| trial, stream an export | per-token `yield` → one ASGI send per JSON fragment; 32,018 sends for 2,000 rows | SERIOUS, confirmed by benchmark | output byte-identical; tests assert equality, not chunk count |
| trial | the behavioural test only proved a function was unused; a `list(...)` would pass | MINOR | the test was weaker than its name |
| cycle 1 | none from the code reviewer; the security pass found the old login bounce leaked a signing capability token into `/login?redirect=` (browser history, access logs) | INFO → fixed by the change | not a failing behaviour, a leak |
| cycle 2 | ticket scoped the 15-minute payment status poller out with the auto-pay; nothing else calls the per-invoice status route, so a bank-rejected manual payment would stay `initiated` forever | HIGH, real | the author's own scoping; a same-vendor review would likely have accepted it |
| cycle 2 | planning doc pseudocode keyed on the retired flag while prod carried a stale `true`; a literal implementation would auto-activate payments without fresh consent | MEDIUM, real | it is a doc |
| cycle 2 | timer installer never disabled removed units; inline status route skipped the dedup key the statement importer relies on | LOW ×2, real | no test covered the installer or the dedup contract |
| ratchet vendoring | argv injection: a changed path beginning with `-` parsed as a flag | SERIOUS | gate code had no tests for adversarial paths |

All `[measured 2026-09-05..07]`. The HIGH in cycle 2 is the cross-vendor axis earning its keep:
the finding was against the ticket, not the code, and the ticket was the author's.

## Cost

Per turn, the review is the largest single block of dev-hat wall-clock: 58 % in cycle 1, 52 %
in cycle 2. Tokens per reviewer: the security side-agent reported 113k and 110k tokens over 19
and 32 tool calls; the cross-vendor reviewer's own accounting is not exposed by its CLI. A
200-engineer shop reports $0.50 to $1.50 per review, halved by session reuse, and would pay a
ceiling of €2 to 3k per developer per month `[field: Pipedrive]`.

Reducing that block is the job of [05-sensor-stack](05-sensor-stack.md): every defect class a
ratchet takes is minutes off the reviewer.

## Report shape

[templates/gate-report.md](../templates/gate-report.md): one row per gate with command, result
and log path; findings with class and disposition; bootstrap failures kept separate from feature
failures; the reachability probe and wall-clock of every model reviewer recorded.
