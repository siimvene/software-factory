# Case study: the head-and-hands harness trial

2026-09-05, kvart, an isolated branch, nothing merged. A validation trial of the delegation
shape: one expensive model as the head (select, design, review, direct remediation, run the
gate), a second vendor's model as the hands (implement, and separately review, fresh process per
call). Full report: [../evidence/kvart-head-hands-trial-report.md](../evidence/kvart-head-hands-trial-report.md).

## The item

Selection was verification-first. The first pick (a credit-note kind-blindness bug in the debt
report) was verified genuinely open but small. An observer flagged the size gap and pointed at
a backlog row: the association-records export built the whole bundle, then held a second whole
JSON string, and returned it in one chunk. Six other "open" medium items were probed and
rejected as already shipped. Finding for the PM: the backlog was stale toward done.

Scope: stream the export via an incremental encoder over a streaming response, byte-identical
output, no row cap (a contractual full copy), no external dependency. Two files, +112/−11.

## The rounds

| Round | Brief | Hands output | Head's correction |
|---|---|---|---|
| 1 | spool-to-disk streaming | 0 edits; the child hung on an inherited open stdin | killed; re-run with `< /dev/null` |
| 2 | streaming via a spooled temp file | endpoint + test, 55k tokens | format not run (would block the commit); ratchet rejected 2 new escape comments; endpoint over 60 lines |
| 3 | redesign: direct incremental stream, no temp file, no escapes | endpoint + test, 48k tokens | lint and types clean, 53 tests green; the cross-vendor reviewer found a SERIOUS regression |
| 4 | coalesce fragments to 64 KiB, strengthen the test | endpoint + test, 43k tokens | 32,018 → 3 chunks, byte-identical |

## What the gates said

| Gate | Result |
|---|---|
| lint, format, types | pass (format after the head's round-2 fix) |
| backend tests, real database | 53/53 |
| red-before | confirmed |
| changed-line coverage ≥ 0.8 | pass |
| ratchets: escapes, conventions, duplication, doc-size, test-hygiene | feature-clean |
| ratchet: complexity | FAIL on a pre-existing function elsewhere (see below) |
| secret scan; dependency scan | pass; no dependency change |
| static analysis | 0 issues on the changed file, run under an isolated project key and deleted after |
| cross-vendor review | 1 SERIOUS + 1 MINOR, both fixed |
| blind security side-pass | none |
| browser QA | N/A, backend-only diff |

**The SERIOUS.** Per-fragment `yield` from the incremental encoder: one worker-thread hop and
one ASGI send per JSON token. Reproduced by the head: 2,000 rows = 32,018 pieces; the reviewer's
10k-row synthetic = 260,009 sends, 17.25 s vs 0.005 s. Green tests and lint missed it because
the output was byte-identical and the tests asserted equality. The cross-vendor reviewer caught
it. That is the trial's headline.

**The MINOR.** The behavioural test only proved the old function was unused; a `list(...)`
would have passed. Fixed with generator-type and chunk-count assertions.

## The complexity gate, and a correction

The ratchet was red on a function in an unrelated maintenance script (complexity 15, 100
lines). The trial report called it "a bootstrap issue, not a feature defect": the baseline had
been recorded on a diverged branch before main commits grew that function.

The session that authored the ratchets verified that reading the next day and corrected it in
an addendum. The function *is* in the baseline, at 10 / 48 lines. On main it measured 15 / 100.
Ratchets fail on new debt and on baselined debt that got worse; this was the second case. The
function had doubled on main after the baseline was taken, and the ratchet caught it. "Bootstrap
artifact" invites the next reader to dismiss a real regression. The remedy is unchanged (split
it, or a person accepts the new numbers in a reviewed commit), but the label matters.

What is true from the original note: an agent must not clear it, and a baseline is tied to the
tree it was taken on, so adopting the gate onto a newer main legitimately requires one
deliberate re-cut by a person recording main's real day-one debt.

## The stall

Post-mortem, measured: 2 h 08 m of the 3 h run was the head sitting idle. It had delegated to
the hands with stdin inherited; the child hung on "reading additional input from stdin"; the
head saw empty output and an empty diff, invented a benign story ("it buffers until exit"), and
ended its turn "waiting for the completion notification". A hung child never completes. Nothing
woke the head until an observer messaged it. The real feature cycle took 24 minutes.

Rules that came out of it, now in the operating contract:

- every delegation carries a wall-clock cap;
- never end a turn on a bare wait for a child process; set a monitor with a timeout that
  re-invokes you and say what happens when it fires;
- empty output plus empty diff is the failure signal, not a curiosity; name the check that
  would prove the benign story (`ps` state, a growing log) and run it, or treat the child as
  hung;
- the child always gets `< /dev/null` or a payload on stdin.

## Evidence-directory gotcha

The duplication ratchet scans the working tree and ignores the ignore file, so a `.py` copy of
the test saved for reviewers in the evidence directory read as a clone of its source. Renamed
off a scannable extension. Keep scratch code off scannable extensions, or teach the walkers the
ignore file (done later, see the sensor stack).

## Cost

Hands tokens ≈ 314k across five calls (stream 55k, remediate 48k, review 69k, security 67k,
coalesce 43k) plus a killed stalled run. The head's own tokens were not available in-session.

## Verdict

The shape works when the head verifies: it caught formatting, escapes and size in round 2 and
directed the redesign; the reviewer caught the regression in round 3; the head reproduced it
with a benchmark before acting. The shape fails when the head waits. The feature was clean on
every gate and left unmerged for the owner's decision; the deeper memory win (not materialising
the row dict before serialising) was deferred and logged.
