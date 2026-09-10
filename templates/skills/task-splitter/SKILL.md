---
name: task-splitter
description: Split a polished, high-scoring ticket (≥85 readiness score) into 2–N independently deliverable sub-tasks, each estimated at ≤ 2 man-days. The original ticket is promoted to an Epic to preserve all context. Invoked from readiness-evaluator option [3], or directly when the user says "split this ticket", "break it up", "too big", "create sub-tasks".
---
<!-- Ported from the reference implementation's PM workspace, 2026-09-10. Generic names per docs/14-pm-surface.md; rename freely, but keep the description's firing conditions, because the description is what decides whether the skill fires. -->

# Task Splitter

Takes a **fully refined ticket** (readiness score ≥ 85) and produces 2–N smaller, independently deliverable sub-tasks, each sized to ≤ 2 man-days.

The original ticket is **promoted to an Epic**: it becomes the container that preserves all the refined context (objective, full AC, scope boundaries, pre-conditions). The sub-tasks are created as child stories/tasks linked to that Epic.

---

## When to split

Split if **any** of the following are true for the input ticket:

- 6+ acceptance criteria that cover independent, separable user flows
- Multiple distinct actors each driving their own workflow end-to-end
- The ticket describes both a user-facing change and an independent backend/API change that could be shipped and tested separately
- The ticket explicitly mentions phases, parts, or "later"
- A feature flag or staged rollout is described, each stage is a natural split boundary
- A dependency chain exists inside the ticket: step B cannot start until step A is done, and A alone has enough scope to ship

**Do not split if:**
- All AC items are part of a single atomic user flow (splitting would leave each sub-task untestable on its own)
- The ticket is already thin, 1–2 days of work
- The only split would be "frontend" vs "backend" with no independent user value. Prefer keeping these together unless the teams are separate and the interface is well-defined

---

## How to split

1. **Re-read the input ticket** in full. Identify the natural fault lines: independent flows, separate actors, sequential dependencies, or rollout stages.
2. **Determine N.** Propose the minimum number of sub-tasks needed so each is ≤ 2 man-days. Do not pad to hit an arbitrary count.
3. **For each sub-task, draft:**
   - Title: clear, actionable, ≤ 10 words, must name its specific sub-scope, not restate the parent
   - Objective: one sentence (what + why, who benefits)
   - Acceptance criteria: 2–5 observable outcome statements (actor + action + expected result)
   - In scope / Out of scope
   - Actor(s)
   - Effort estimate: S (≤ half day), M (1 day), L (2 days). Flag anything > L, it needs further splitting.
   - Dependencies on other sub-tasks in the set (e.g. "depends on Sub-task 1"), or "none"
4. **Coverage check:** The union of all sub-task scopes must equal the original ticket's scope. Explicitly call out any part of the original that could not be cleanly assigned.
5. **Independence check:** Each sub-task should be deployable and testable on its own, except where a stated dependency exists.

---

## Output format

```
## Split proposal: [Original ticket title]
Parent ticket: [KEY] (will be promoted to Epic)
Original scope: [one-sentence summary]
Proposed sub-tasks: N

---

### Sub-task 1: [Title]
**Objective:** [What + why, who benefits]
**Effort estimate:** [S / M / L]
**Depends on:** [Sub-task N, or "none"]

**Acceptance criteria:**
- [Actor] can [action] and [observable result]
- [...]

**In scope:** [bulleted list]
**Out of scope:** [bulleted list]

---

### Sub-task 2: [Title]
[same structure]

---

### Coverage check
- ✅ All original AC items assigned: [yes / no, list any gaps]
- ✅ No sub-task exceeds L (2 days): [yes / no, flag any]
- ✅ Each sub-task is independently shippable: [yes / no, explain any exceptions]
```

---

## After showing the proposal

Always pause and confirm before taking any action:

```
Does this split look right?

  [1] Looks good, promote [KEY] to Epic and create N sub-tasks under it.
  [2] Adjust: [describe what to change].
  [3] Cancel: keep the original ticket as-is.
```

### If [1] confirmed: tracker write sequence

Use the `tracker-mcp` skill for all writes. Follow the Preview → Confirm → Execute → Log pattern for each step.

**Step 1: Promote original ticket to Epic.**
- Edit the original ticket's issue type to `Epic` via the tracker MCP `edit-issue` operation.
- Keep all existing fields (summary, description, AC, labels) unchanged, the refined content is the value of the Epic.
- If the project does not support changing issue type to Epic, create a new Epic with the same content and note the original ticket key in its description.

**Step 2: Create each sub-task as a Story (or Task if Story is unavailable).**
- Use the tracker MCP `create-issue` operation for each sub-task.
- Populate: summary, description (objective + AC + scope), issue type.
- Link each new issue to the Epic using the tracker MCP `link-issue` operation with the appropriate link type (`is child of`, `belongs to epic`, or `relates to`, use whichever is available in the project).

**Step 3: Log all actions.**
Append to `~/tracker-actions.log`:
```
────────────────────────────────────────
[ISO-8601 timestamp]
ACTION:   Task split
EPIC:     [KEY], [Summary] (promoted to Epic)
CREATED:  [KEY-1], [Sub-task 1 title]
          [KEY-2], [Sub-task 2 title]
          ...
RESULT:   ✅ Success
────────────────────────────────────────
```

**Step 4: Confirm to user.**
```
✅ Split complete.
  Epic:  [KEY], [Original title]
  Tasks: [KEY-1], [KEY-2], ... (linked to Epic)
```

### If [2] adjust
Revise the proposal inline, apply only the stated changes, do not regenerate from scratch. Re-show the updated proposal and ask for confirmation again.

### If [3] cancel
Acknowledge and stop. Do not create or modify anything in the tracker.

---

## Guardrails

- **Only split along lines already present in the ticket.** Do not introduce new scope, new actors, or new AC that were not in the original.
- **The Epic retains all original refined content.** Never strip the description or AC from the parent when promoting it.
- **Each sub-task title must differ from the Epic title** and name its specific sub-scope.
- **Effort estimates are rough.** If unsure, err toward L (2 days) and flag it.
- **Do not skip the confirmation prompt.** Always show the proposal and wait for [1]/[2]/[3] before writing to the tracker.
