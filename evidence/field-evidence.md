# Field evidence

External, public sources the design leans on. Nothing here was measured by this design; each item
is marked `[field: <source>]` and carries its numbers and its caveats. Compiled 2026-09-07 from the
flywheel design notes (sections on field evidence and on upstream deltas), the operator memory store,
and the consort README.

---

## 1. Pipedrive AI code review at 200 engineers `[field: Pipedrive]`

**What it is.** A public podcast interview (Algorütm episode 349, mined 2026-09-04) with Pipedrive's
dev-productivity lead and an AI platform engineer. About 200 engineers, Claude plus GitHub Actions,
AI review running in production. Same region, real scale, so it is the closest external anchor to
the verify layer proposed here.

**What they run.**
- Cross-vendor and narrow-scoped multi-agent review, live: Claude orchestrates, an OpenAI model does
  a pass, scoped sub-agents feed the orchestrator, the author model self-reviews. Their reasoning:
  "if one is compromised it's caught".
- Criticality-tiered auto-approve: low-criticality services get AI approval and auto-deploy, critical
  services need human sign-off before live.
- The same review runs locally (as a marketplace plugin) before the PR and again in CI, one artifact.
- Plugin per concern, dynamically dispatched (accessibility, React performance as separate plugins;
  conditions in the prompt fire the right sub-agent).
- The review reads architecture guidelines from CLAUDE.md plus a cross-service architecture-decision
  aggregator: a crawler agent builds one reference and dependency map and flags downstream break risk.
- A ticket and description quality gate: the review flags a poor ticket or PR description ("I don't
  understand the intent, improve it").

**Numbers.**
- Primary review-quality metric is recommendation acceptance rate: parse each PR, did the developer
  act on the AI comment (a commit) or dismiss it. Pipedrive measures about 70 % acted upon.
- North-star lagging metric is defect injection rate (bugs per PR) plus SLA. Both held or improved
  while PR volume roughly doubled in a year. They credit AI review for making the flood reviewable.
- Cost anchor: about $0.50 to $1.50 per review. Session reuse halves it, extra sub-agents add
  overhead. Ceiling they would still pay: about EUR 2,000 to 3,000 per developer per month.
- Model choice: Opus 4.6 at max effort is their price and quality sweet spot. The newest model
  roughly doubled cost without doubling quality, so they rolled back. An alternative harness on the
  same model benched 20 % to 30 % cheaper. Cost is watched on a daily per-developer dashboard with
  threshold alerts.

**What this design takes.** Acceptance rate as the leading indicator for review quality, and defect
injection rate as the lagging one. The per-review cost band as the sanity check on the cost model.
The criticality tier maps onto the money-path gate. Local-before-PR plus CI on one artifact is the
same shift-left shape as the devcontainer plus a local consort run.

**Caveats and risks they hit.**
- Vendor API instability breaks the whole workflow, and they have no cross-vendor fallback: it fails,
  posts "retry", a human re-triggers. This confirms that hard-fail rather than silent degradation is
  a real requirement, and that a lights-out loop needs an explicit fallback and retry policy.
- Model updates change behaviour unpredictably ("a casino"). One Claude Code update made the review
  agent post an "all done" emoji without submitting the review. They added a hook that verifies the
  review was actually posted. This is the strongest external argument for evals on the agent-config
  surface and for verifying the effect of a gate rather than trusting the agent's self-report.
- Prompt injection via committed "new agent instructions" is untested there ("we trust the developer").
- Quota gaming: with per-developer token quotas, developers offloaded feature building onto review
  tokens (stub, then `/review`, then "now implement it"). Worth knowing before setting quotas.
- Build versus buy, their advice: under about 20 developers do not build, buy. Build only at scale,
  and budget a dedicated role plus behaviour visibility, not a half-day setup. Keep human review on
  complex or critical work, because PR review is also knowledge transfer and full automation there
  loses it. Plugins over-fire if their description is too generic, so add explicit firing conditions.

**Provenance caveat.** This is a single interview, self-reported, not an audited study. The 70 %
acceptance rate is their own parse of their own PRs.

---

## 2. Deltas from Anthropic's published AI-native SDLC `[field: Anthropic AI-Native SDLC]`

**What it is.** Anthropic's published AI-native SDLC playbook and its security post, read against
this design in 2026-09 to find what is missing here rather than what is already shared.

**What the design takes (four deltas, folded into the standard rather than into one team's setup).**
1. Evals on the agent-config surface: gate changes to the agent contract, rule packs, CLAUDE.md and
   skills behind an eval suite, and turn each incident into a permanent eval. Rated the biggest
   missing piece, because it protects the standard itself. Their framing: "monitoring bugs becomes
   monitoring loops."
2. Security shifted left to SPEC: a lightweight product-security review (design against a
   MITRE-style checklist) at the ticket stage, not only pre-merge. Load-bearing given the legacy
   core's confirmed unauthenticated endpoints and committed secrets.
3. Western Electric control bands for the maintain edge: 1 sigma log, 2 sigma read-only diagnose,
   3 sigma propose a fix PR. Sharper than a coarse canary.
4. Managed settings plus a scoped bot identity as the enforcement tier above local hooks. The
   devcontainer template already carries managed settings and an egress gateway, so this is about
   80 % done; a local pre-push guard is the stand-in until the scoped bot identity lands
   (contents and PR write, nothing more).

**Where this design is already ahead, and keeps its choice.** Cross-vendor review (their published
loop stays single-vendor), pointer-only memory with a promote-PR gate, and the team-context
knowledge plane.

**Caveat.** These are deltas read off published material, not a measured comparison of two running
systems.

---

## 3. Uber Engineering: outcome-denominated metrics at 70 % agent PR share `[field: Uber Engineering]`

**What it is.** A summary of Uber Engineering's "Running a Software Factory Efficiently at Uber
Scale" (2026-09-04), recorded in the operator memory store on 2026-09-05.

**Numbers.** 70 % of PRs come from agents. Usage is up 7 times since February. Total spend flattened
in April.

**The metric set.** Cost per agent outcome rather than per session: cost per merged PR, cost per code
review, cost per alert triaged. Each is paired with a quality signal, either revert rate or F1
(precision and recall). These replace per-token spend as the primary metric once agents dominate PR
volume.

For an adversarial review agent, Uber scores the agent against real PRs with known bugs: precision is
the fraction of flagged issues that are real bugs, recall is the fraction of real bugs caught, and
cost per catch sits alongside. They then run whatever is Pareto optimal on quality against cost and
re-benchmark as models improve. Model choice becomes a data problem rather than a preference.

Revert rate tracks whether agent-generated PRs are stable after merge. A high revert rate is a quality
regression even when throughput metrics look good.

**What this design takes.** Four pre-requisites, all of which must happen before agents dominate:
1. Baseline the revert rate now, on human-written code, because there is no comparison point later.
2. Baseline the defect escape rate now (bugs reaching production).
3. Define an F1 test set for the adversarial reviewer: real PRs with known bugs, run the reviewer
   against them to calibrate precision and recall before trusting the gate.
4. Track cost per feature, not cost per PR, because an agent may churn 5 PRs for one feature.

**Caveat on transfer.** Uber optimises per-token spend; a subscription-funded setup cannot copy that
part. The quality signals do transfer exactly: revert rate, defect escape and F1 are
subscription-agnostic. Under a subscription, cost per feature is the monthly subscription divided by
features delivered, which measures subscription efficiency rather than marginal cost.

---

## 4. SWE-chat 4-tool study: 93.4 % of issues caught by exactly one tool `[field: SWE-chat 4-tool study]`

**What it is.** The study cited in the consort README as the reason cross-vendor review is the
point: in the SWE-chat 4-tool study, 93.4 % of issues were caught by exactly one tool.

**What the design takes.** Two model families do not share blind spots, so a second reviewer from a
different vendor is not redundancy, it is coverage. This is the empirical backing for the cross-vendor
axis of the verify gate, and for the rule that every substantive artifact gets touched by both the
principal and a different-vendor implementer or reviewer.

**Caveats.** The figure is quoted second-hand through a tool README, and the study measured static
analysis and review tools rather than this specific pairing of models. It supports the direction
(low overlap between independent checkers), not the exact overlap rate for any given pair. The
locally measured analogue is the cycle-2 finding: an author-side model accepted a scoping the
cross-vendor reviewer rejected as a HIGH.

---

## 5. ponytail: a YAGNI ladder for the builder `[field: ponytail]`

**What it is.** ponytail, an MIT-licensed Claude Code and Codex plugin (public GitHub repo), recorded
in the operator memory store on 2026-09-07 as a builder-side candidate. It installs a 7-rung decision
ladder into the agent before it writes code: does this need to exist at all, is it already in this
codebase, does the standard library do it, is there a native platform feature, is it in an installed
dependency, is it one line, and only then the minimum that works. Its own framing is "lazy, not
negligent": security, validation, error handling and accessibility are never on the chopping block.

**Numbers (the plugin's own benchmark, real agentic sessions, FastAPI plus React, Haiku 4.5, n = 4).**
- 54 % fewer lines of code (mean), up to 94 % fewer on over-build traps (a hand-built date picker
  collapsing to `<input type="date">`).
- 20 % lower cost, 27 % less time, 100 % safe on their scoring.
- Near-zero reduction on already-minimal code, which is the appropriate result.
- Referenced from a social post with about 273,000 views. Version 0.3.8 at the time of recording.

**What the design takes.** Agents have infinite energy and zero maintenance trauma, so a pre-write
ladder injects the trauma. It pairs with a deterministic map of the codebase: ponytail asks "does
this already exist?" and a structural index answers in roughly 580 tokens rather than 40,000 tokens
of agent grepping. It complements the duplication ratchet, which catches duplication after the write,
by preventing it before the write. Under a subscription, less code compounds: less code means less
future agent work means less limit burn.

**Caveats, all unresolved at the time of recording.**
- "Made my agent lazy" was the top reply on the launch post (3,700 likes). The ladder may suppress
  necessary code on complex tasks. The benchmark is a generic FastAPI plus React template, not a
  large domain system. If the builder skips needed validation because the ladder called it
  unnecessary, that is a quality regression the benchmark cannot see.
- Two separate commenters reported that a plugin-security scanner refuses to install it, one flagging
  it as insecure. The plugin installs Node.js lifecycle hooks, which is the attack surface. Inspect
  the hooks before trusting it, and do not install it globally before verifying.
- Its patterns were written for a small model and may constrain a stronger one, the known
  "weak-model workarounds poison strong models" failure.
- Status: trial required on a real repository with a complex multi-file task before any production
  adoption. Not adopted on the strength of the benchmark alone.

---

## 5a. chisle replaces ponytail on the reference implementation `[field: chisle]`

**What it is.** chisle, an MIT-licensed Claude Code and Codex plugin (rules also ship for six
other agents), version 3.0.0 released 2026-07-28, zero runtime dependencies, 136 GitHub stars on
2026-09-10. It carries the same 7-rung ladder as ponytail: does this need to exist, reuse what is
in the codebase, stdlib, native platform feature, installed dependency, one line, only then the
minimum that works. It adds a zero-fluff prose ruleset injected at session start (about 1,600
tokens once, a 50-token reminder per prompt) and a post-tool-use compressor for shell, agent,
grep, glob, web and MCP output: over 8,000 characters the middle is elided, 60 head and 40 tail
lines and up to 12 error-like lines survive, and a byte-identical repeat becomes a marker. Read
and Edit results are never touched.

**Numbers (the vendor's own comparison, 20 tasks in two suites, Haiku and Sonnet, billed output
tokens as % of the no-tool baseline).**

| | total bill | average task | worst case | worse than no tool |
|---|--:|--:|--:|--:|
| caveman | 80 % | 98 % | 424 % | 6 / 20 |
| ponytail | 68 % | 91 % | 227 % | 8 / 20 |
| chisle | 52 % | 69 % | 173 % | 1 / 20 |

- Tool output was 67.5 % of session context on the vendor's corpus; the compressor claims about
  46 % smaller per eligible output, and the saving repeats on every later request in the session.
- The vendor states its own caveats: the largest single drop in its coding table came from asking
  which framework instead of guessing, and the 3.0.0 ruleset differs from the one the committed
  benchmark cells were measured on.

**Why it replaced ponytail.** The ladder was the reason for adopting ponytail; chisle has the same
ladder with a smaller and rarer downside on these numbers, and it adds the input axis nothing else
in the stack touches. This is the vendor of one tool benchmarking the other on generic prompts:
field class, not measured here.

**Pre-adoption audit on kvart `[measured 2026-09-10]`.** Hooks and plugin manifest read in full:
no child process spawn; one 1.5 s update check against the npm registry at session start, disabled
by an environment variable; state files only under the Claude config directory, refusing symlinks.
Skill exfiltration scan: 0 findings in 59 files. Marketplace source pinned to tag v3.0.0; the
format accepts a tag or branch, not a commit, so the pin is a tag; the cached plugin content was
verified to match the tag's commit, not the branch head, which carries one commit past the tag.
The two-vendor review of the swap found one HIGH each, the same finding: the first commit left the
source unpinned, the second commit fixed it. A headless session receives the activation message
from the session-start hook.

**Open.** As for ponytail: a trial on a complex multi-file task before any rollout beyond the
reference implementation. New: whether elided tool output ever hides an error line the agent
needed; the 12 salvaged error-like lines are a heuristic.

## 6. enola: architectural regression testing `[field: enola]`

**What it is.** enola (Apache 2.0, public repo, CI passing), recorded in the operator memory store on
2026-09-07. It maps codebase structure before a change and compares after, reporting only what this
change introduced rather than existing debt. Recommended for cross-repo use by a staff engineer at a
large marketplace, as a complement to a structural index rather than a replacement. No model, no
embeddings, no upload: one binary, an MCP server, and agent hooks via `enola install --hooks`.

**Numbers and shape.** 19 explainers (checks), and the adopter configures which ones fail the build.
Three are provably certain at confidence 1.00: `cycles` (circular dependencies), `layers` (declared
layer order violations) and `intent` (undeclared cross-repo seams, or declared ones never measured).
Everything else is heuristic and capped at 0.95, so gating on those needs an explicit
`--min-confidence`. Other explainers: `crossrepo`, `god-class`, `hotspots`, `complexity-outliers`,
`unused-routes`, `messaging-coverage`. Out of the box the policy is to fail nothing: every finding is
reported with exit 0 until the adopter names what should break. Recommended starting gate is
`--fail-on=layers,intent,cycles`, the three provable ones.

**What this design takes.**
- The scope spillover gate: the intake stage declares a target scope, and after the build the shipper
  runs `enola check --target=<scope> --max-spillover=0`. If the builder touched code outside the
  declared scope the gate fails. Zero inference, exact measurement. This is an executable boundary at
  the architectural level.
- The cross-repo angle: in a group of services and repos, a builder in one repo importing from
  another without declaring the dependency still builds and still passes tests, while the
  architectural contract is broken. `crossrepo` plus `intent` catch that, and per-repo tools do not.
- `enola doctor` verifies that hooks actually fired, not merely that they are configured. Same
  principle as proving the reviewer ran.
- Position in the stack: a structural index orients before the write, enola validates architecture
  after it. A quality ratchet catches code quality (complexity, escapes, duplication), enola catches
  architectural integrity (layer violations, cycles, scope spread). Same ratchet principle, different
  dimension, and the hooks coexist.

**Caveats.** Only 3 of 19 explainers are certain; the other 16 are heuristics and should not gate
without a confidence floor. The tool is young, and the recommendation above is one engineer's, not a
study. Nothing here is a measured result on this design's own repositories.

## 7. Horthy, "Harness Engineering is not Enough: Why Software Factories Fail" `[field: Horthy]`

**What it is.** A 19-minute conference talk (AI Engineer World's Fair, published 2026-07-23) by
the founder of HumanLayer, a company selling an agent collaboration workspace. It expands two
public threads from 2026-07-24 and 07-25 that the operator assessed against the group's built
estate on 2026-07-26. The speaker sells a plan-heavy product, so the plan-heavy conclusion is
also a product story; the argument stands on its own and is recorded here for the argument.

**The argument.** Coding models are trained by reinforcement on a reward of the shape "the hidden
tests pass and nothing regressed". The speaker walks through a multilingual issue-resolution
benchmark: base commit checked out, the agent's edits to test files reverted, the held-out test
patch applied, binary reward. Nothing in that reward prices architecture, whose cost arrives
months later, so a model gets better at passing tests and no better at keeping a codebase
changeable. His own company ran without human code review from July 2025 and paid with an
outage in code nobody had read for three months. Conclusion: restore human review and make it
cheap by deciding earlier, in four phases (product review, architecture, program design down to
types and call graphs, vertical slices), on the estimate that 30 minutes of alignment saves
hours of review. Two admissions on stage: the maintainability claim is experience, not a
benchmark result; the three-to-six-month horizon is anecdote.

**What this design takes.**
- The durable justification for [adr/0003](../adr/0003-cross-vendor-non-inheriting-review-is-the-merge-gate.md)
  and [adr/0006](../adr/0006-pr-gated-output-human-release.md): a review gate does not sunset with
  model releases, because the training signal has no maintainability oracle. Field evidence, not
  measured here.
- Program design as a named stage ([02-loop](../docs/02-loop.md),
  [adr/0010](../adr/0010-program-design-before-the-plan.md)). The phase is the speaker's; the
  sizing rule, the template and the two mechanical checks are this design's own.
- The check from a public evaluation the talk cites (FrontierCode): an agent-written test must
  fail against the pre-patch code, or it has not shown it detects the behaviour the patch
  repairs. This design's fail-on-base check ([05-sensor-stack](../docs/05-sensor-stack.md))
  generalises it to every new or changed test, with declared exemptions and the failure kind
  recorded.
- Review as rework: a pull request whose decisions were not agreed forces the reviewer back into
  design. The rework-share metric in [10-measurement](../docs/10-measurement.md) is how this
  design will tell whether the note pays.

**Caveats.** No number in the talk is a measurement on this design's repositories. The speaker
attributes one agent runtime's commercial rise to training against its own harness: plausible,
unverified, and irrelevant to the gates here. The speaker's target is a factory with no human
code review at all; this design never proposed one (the human gate is a decision on evidence,
[01-principles](../docs/01-principles.md) §4), so the talk argues for the design's shape rather
than against it, and its two named gaps are what [adr/0010](../adr/0010-program-design-before-the-plan.md)
closes.
