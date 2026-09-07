<!--
  DELEGATION BRIEF. Written by whoever is about to hand work to a subagent or a second
  session. The subagent sees only this text: no memory of the conversation that produced
  it, no visibility of what surrounds it. Anything not written here does not exist for
  the executor.
  Skip the ceremony only for a single-file lookup. Everything longer gets all five parts.
-->

# Delegation brief: <task name>

## 1. Goal

<One sentence naming the outcome that counts as done. Not the activity, the outcome.>

## 2. Paths

- Working tree: <absolute path, or the worktree to create first>
- Files to read: <paths>
- Files that may be changed: <paths>
- Files that must not be touched: <paths>
- Where artifacts go: <directory for logs, reports and screenshots>

## 3. Constraints

- Surface allowlist: <paths, services, APIs>. Everything unlisted is denied.
- Wall-clock cap: <n> minutes. Wrap the work in a timeout so a hang becomes an observable
  failure rather than a silent stall.
- Spend cap: <amount, or "none; no paid surface in scope">
- Methodology: <rules the executor must follow, for example: write the failing test first;
  verify the fix against the reverted code; never push, never merge, never deploy>

## 4. Definition of done

<The mechanical check that proves completion, as a command with its expected result.
Prefer a command over a judgement: "tests green" beats "looks right".>

```
<command>
# expected: <exact expected output or exit status>
```

## 5. Return format

At most 10 lines. State what you observed, not what you did. Verbose output stays on disk
at the artifact path above; the return is a summary plus pointers.

## Mandatory phrases

Include these three lines verbatim in every brief. They are the difference between a
subagent that finishes its own loop and one that hands its unfinished work back up.

- Iterate until you observe the target OR hit a blocker only the owner can resolve.
- Do not return with "someone should check X"; check X yourself before returning.
- If your tool budget is running low, do a partial verify NOW and return what you actually
  observed.

## Notes on shape

- Never end a turn on a bare wait for a child process. If the only next step is waiting,
  set a timer that will wake you and say what happens when it fires.
- Empty output plus an empty diff is a failure signal, not a curiosity. Name the check that
  would prove otherwise and run it; if there is no such check, treat the child as hung.
- When verification is expensive, split the work: one brief ships and returns hashes plus a
  one-shot state check, a second brief verifies after the soak time and is read-only.
