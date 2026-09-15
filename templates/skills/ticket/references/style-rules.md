# Style rules for tickets

Eleven rules, read before every draft. Ported from the reference implementation's PM workspace on 2026-09-15, where the skill had referenced this file since 2026-09-07 without it existing (recorded in docs/14-pm-surface.md). They are corrections collected from reviewed tickets, so on a
conflict with the template they win. Numbered so a review can cite one.

1. **Title names the scope, not the work.** 3 to 8 words, sentence case, no trailing punctuation,
   one of the template's title patterns. Never "Update", "Fix", "Changes to", never "As a", never a
   ticket key in the title.
2. **Context answers why now.** Two to four sentences of motivation. A link, a ticket key or a
   restatement of the title is not context.
3. **Acceptance criteria are observable.** Each bullet names a state, an action and what is visible
   afterwards, with the exact value where a value is involved. No implementation instructions
   ("place the script in the head"), no vague verbs ("handles", "processes", "resolves") without an
   object.
4. **Exclusions are written down.** At least one "Out of scope:" bullet naming the thing a reader
   would assume is included. Edge cases are labelled "Edge case:" and sit in the criteria, not in
   Other information.
5. **Permissions live in the criteria.** Which role or permission string gates each flow is a
   behaviour, so it is a criterion, never a note.
6. **Nothing that is not in the source.** Every criterion traces to the spec or to a recorded
   product decision. Logging, monitoring and "ops visibility" extras are the usual smuggled
   requirements; cut them unless someone asked.
7. **Real vocabulary only.** Use the names the code and the team use (the names the domain model and the
   team already use); never invent a category. When the spec and the code
   disagree on a name, the code wins and the draft says so.
8. **Say the gap, not the plumbing.** Do not explain how the system currently resolves, falls back
   or propagates anything; the reader has the code. State what changes.
9. **No obvious bullets.** If a mid-senior developer on this team would say "yes, obviously", cut
   it. A general rule is not restated with examples.
10. **Claims about current behaviour cite a path.** "Preserves legacy behaviour" needs a file or
    class reference; a naked "as is" is a gap, and the skill checks the code before writing it.
11. **Technical shape stays out.** Endpoint design, service ownership, request and response format
    are grooming decisions: mark `[dev / grooming]` in the open questions, never in the ticket.
    Assignee, priority, sprint and points are never in a draft. Issue type, project, epic parent,
    labels and links are, with a reason each (step 4b).
