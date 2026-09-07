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
4. **Browser QA pass** on every UI surface the diff touches, as the right persona, in a real
   browser, checking rendering, console, interactions and locales; findings with screenshots.
5. **Adjudication.** Spot-verify every CRITICAL and SERIOUS claim against code. Fix those before
   push. Log MINOR with a disposition. Disbelieve at least one rejected finding per panel.

Exempt: docs-only and memory-only commits. A docs commit that encodes a security rule or a data
model decision is reviewed anyway.

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
