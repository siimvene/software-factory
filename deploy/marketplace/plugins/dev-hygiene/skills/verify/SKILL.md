---
name: verify
description: Evidence-based completion check before claiming work is done. Use when about to say a task is complete, fixed, deployed, or working; when the user asks "are you sure?" or "did it work?"; or before opening a PR. Do not use for planning or mid-task status updates.
version: 0.1.0
---

# verify — no completion claims without fresh evidence

Intent is not completion. Execution is not verification. Only observed output
is truth.

## The loop

1. **Name the claim.** What exactly are you about to assert? ("tests pass",
   "the endpoint returns 200", "the config is applied")
2. **Name the command that proves it.** If you cannot name a mechanical check,
   the claim is an opinion — downgrade it to one explicitly.
3. **Run it fresh.** Output from before your last change is not evidence.
4. **Read the full output.** Exit code 0 with a failure in the text is a fail.
5. Only then state the claim — with the evidence, not instead of it.

## Minimum evidence by change type

| Change | Minimum proof |
|---|---|
| Code edit | build/lint + the relevant test suite, run after the final edit |
| Bug fix | the reproducing case, failing before, passing after |
| Config/service change | process/service state actually inspected, not assumed |
| Doc/spec change | rendered/linted output, links resolve |

## Red flags — verify immediately, don't argue

- You wrote "should work", "should be fine", or "probably" about system state.
- The user asks "are you sure?" — treat it as a failed audit, re-verify.
- Multiple changes summarized in one claim — verify each, not the batch.
- Time has passed or context was compacted since the check ran.

## Then attack it

After evidence is in hand: argue against everything you just concluded. Find
the weakest point — the untested edge, the environment difference, the test
that passes for the wrong reason. If the attack lands, say so and keep working;
if it doesn't, ship the claim with its evidence.

This skill reports and verifies. It never commits, pushes, or marks tickets.
