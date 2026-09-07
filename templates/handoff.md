<!--
  SESSION HANDOFF. Written at the end of a session by the agent that ran it, read cold by
  the next session or the next person. Write it when the task arc is complete, nothing is
  queued or half-applied, and the session has burned enough context that a fresh start
  with curated notes beats continuing on summaries.
  The test for every line: would a reader who knows nothing about this session be able to
  act on it? If not, cut it or add the missing fact.
-->

# <topic> handoff, <YYYY-MM-DD>

**Supersedes:** <previous handoff, or "none">. <One line saying what the previous one is
still good for, if anything.>

**Reach:** <what is local only, what has been pushed, what is live>. State this first: the
most expensive wrong assumption a cold reader can make is about where the work already is.

## Trees and branches

| Tree | Branch | At | State |
|---|---|---|---|
| `<path>` | `<branch>` | `<sha>` | <n commits, clean or dirty, pushed or local> |
| `<path>` | `<branch>` | `<sha>` | |

## Done and verified

<!-- Only what was verified by running something in this session. For each item name the
     check that proved it and the number it produced. Work that was done but not verified
     goes under "deferred findings", not here. -->

- **<thing>:** <what it does now>, verified by `<command>`, result <number or state>.
- **<thing>:** <...>

## Gotchas

<!-- The traps that will cost the next session an hour. Each one names the symptom, the
     cause, and the exact workaround. Order by how much time it saves, not by when it was
     discovered. -->

- **<symptom>:** <cause>. <Workaround, as a command where possible.>

## Decisions waiting on the owner

<!-- Things an agent must not decide: money, external commitments, credentials, authority
     boundaries, anything that changes what a person is accountable for. Each entry says
     what is blocked until the decision lands. -->

1. **<decision>:** <what is blocked by it>, <what the options are>.

## Deferred findings

| Finding | Severity | Disposition | Owner |
|---|---|---|---|
| <what> | <CRITICAL/SERIOUS/MINOR> | <ACCEPT-DEFER/ACKNOWLEDGE> | <role> |

## Verify on arrival

<!-- A block the next session can paste before trusting a word of this document. Every
     command has its expected answer in a comment, so a drifted state is visible in one
     pass rather than discovered halfway through the next task. -->

```sh
<command>   # expected: <value>
<command>   # expected: <value>
```

## Memory search hints

<!-- The queries that surface the durable claims behind this work, so the next session
     does not rediscover them. Terms, not prose. -->

- `<search term>`
- `<search term>`
