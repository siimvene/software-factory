---
name: meta-reasoning
description: Structured reasoning discipline for complex or high-stakes problems — decompose, solve with confidence levels, self-refute, synthesize. Use for architecture decisions, tricky debugging hypotheses, or when the user asks to think carefully / meta-reason / sanity-check a conclusion. Skip for simple factual questions.
version: 0.1.0
---

# meta-reasoning — decompose, weigh, refute

For complex problems only; simple questions get direct answers.

1. **DECOMPOSE** — break the problem into independent sub-problems. Name the
   dependencies between them.
2. **SOLVE** — address each with an explicit confidence (0.0–1.0) and the
   evidence that confidence rests on. Distinguish verified facts from
   assumptions — an unverified assumption caps confidence at 0.6.
3. **REFUTE** — argue against everything you just concluded. Attack the
   weakest sub-answer first: what evidence would change it? Is that evidence
   cheap to get? If yes, get it before proceeding.
4. **SYNTHESIZE** — combine using the weighted confidences; the chain is only
   as strong as its weakest load-bearing link (name that link).
5. **REFLECT** — if overall confidence < 0.8, state the specific weakness and
   either fetch the missing evidence or present alternatives instead of a
   single answer.

Always output: the answer, the confidence, the key caveats, and the one thing
that would most change the conclusion.

This skill produces analysis only — it makes no edits and takes no actions.
