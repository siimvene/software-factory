# 0012. Money paths are mapped end to end, and every exit agrees

- **Status:** proposed
- **Date:** 2026-09-28
- **Deciders:** the operator, the principal session that proposed it

## Context

The design tiers the money surface per class ([09-legacy-adoption](../docs/09-legacy-adoption.md)
§d, [18-flightlist](../docs/18-flightlist.md) P2). A surface file lists the code where a wrong
change moves wrong money (transaction tier) or shows wrong numbers people pay on (reporting tier),
and the tier sets human sign-off and mutation targets. The tier answers which code is money.

It does not say how one figure travels. A figure is created by an input, then parsed, computed,
rounded, stored, advanced by a job, serialised, rendered and sent out, and it reaches several
exits where a person reads it or pays it. Nothing in the design names those hops, the test that
holds each one, or the test that proves the exits agree.

One measured miss sits exactly in that gap. Cycle 2 retired a money path, and its ticket scoped a
15-minute poller out together with the auto-pay. The poller was the only hop that moved a manual
payment from `initiated` to settled or rejected: no view called the per-invoice status route, so
an abandoned or bank-rejected payment would have stayed `initiated` forever and blocked every
retry. The poller was on the money surface. The cross-vendor reviewer caught it in the diff
stage, HIGH `[measured 2026-09-07]`. Nothing earlier could have, because no artifact said the
poller was the hop that closed that state.

One measured precursor exists. The legacy core's first characterization target was a price
recalculation service that compares 20 money extractors across two states; its suite killed 68
of 68 mutants `[measured 2026-09-04]`. That is an agreement test in all but name, inside a single
class.

The field source states the rule directly `[field: Aruannik]`. When a product's figures come from
uploaded bank statements and invoices, they have to be followed through parsing, calculation, the
browser and the finished report, and "they all have to agree". Before an accounting change that
project requires a map of those paths and their tests, which "gives the agent something concrete
to preserve". The write-up publishes no measurement of what the map caught.

## Decision

We will keep a money path map beside the money surface, check it mechanically, and make it the
money-lane input of the program design note and of the review.

1. **The map.** A `money-paths.yaml` in the code repository, next to the surface file, in the
   shape of [templates/money-paths.yaml](../templates/money-paths.yaml). One entry per figure or
   payment state people pay on: an invoice total, a per-unit charge, a payment's status. Each
   entry lists its entry points, its hops in order, and its exits. A hop is anything that reads,
   transforms, advances or displays the figure, scheduled jobs included. Every location, entry,
   hop and exit alike, names its file and symbol, so a diff anywhere on the path can be matched
   to it. A hop also names what it does to the figure, its rounding rule where it rounds, and the
   test that holds it. A hop that runs only because something registers it (a scheduled job, a
   route, a queue consumer) names that registration too, as `wired_by`: the file and the line
   that wires it.
2. **The agreement test.** One per entry, parametrised by exit. One input, then the figure
   asserted at every exit: the stored value, the API response, the view, the rendered document,
   the outbound file. Each exit names its own test node id (the agreement test's case for that
   exit), so the map binds every exit to an assertion a script can see. The exits are asserted
   equal to each other and to a hand-computed expected value taken from a numbered example. Agreement between exits alone is not enough, because a calculation that is wrong at
   the source stays consistently wrong at every exit. The money lane's mutation targets apply to
   the hops it covers.
3. **The resolver.** A script, self-testing like the surface predicate: it withholds all output
   if a planted case misclassifies. It checks that every location's file and symbol resolve in the
   tree; that every hop's test and every exit's test node id are collected by the test runner;
   that every `wired_by` line still exists in its file; and that every file on the transaction
   tier is a location of some entry or is declared off-path with a reason. A registration that
   lives outside the repository (a timer unit on a host) is reported as unchecked, never as
   resolved. The resolver runs on Day 1 and on every diff that touches the map or a mapped file.
   What it cannot see is whether an assertion is strong; that is the mutation target's job.
4. **Retiring a hop breaks the map.** A diff that deletes a hop's symbol, removes its
   registration, or drops an exit's test case fails the resolver until the same diff updates the
   entry: the hop is replaced by a named one, or the state it advanced is shown closed elsewhere.
   Cycle 2's poller is the case this rule exists for, and its failure mode was the registration:
   a poller whose file, function and unit test all survive while nothing schedules it any more
   closes nothing. `wired_by` is what makes that removal visible.
5. **The diff selects the path.** A diff that touches any mapped location, entry, hop, exit or
   registration, adds that entry's hop tests and every exit case of its agreement test to the
   selected set of the receipt-checked pre-push gate, as must-pass on the branch. They exist before the change, so the fail-on-base check
   ([adr/0010](0010-program-design-before-the-plan.md)) treats them as declared characterization
   tests, never as red-first tests.
6. **Note and review.** On a full-size money ticket the program design note fills section 8: the
   entries touched, the hops changed, the figure expected at each exit before and after on the
   numbered example, and the map diff. The touched entries travel to the review panel as one more
   injected pack ([adr/0009](0009-the-spec-is-a-gate-input.md)), so a hop changed but not declared
   is a `spec-drift` finding on the money lane, classified by the normal severity rule.

Scope: repositories with a tiered money surface. Reporting-tier figures get the map and the
resolver. The agreement test and its per-exit cases are required on the transaction tier; on the
reporting tier an entry may say `agreement_test: none` with a reason, and the resolver then
reports its exits as unasserted, advisory, instead of failing.

## Consequences

- **Positive:** "what else carries this figure" is answered from a file before the diff exists,
  not discovered by the reviewer after it; a retirement cannot silently drop the hop that closes
  a state; every exit has a named assertion against a hand-computed value; the builder gets the
  concrete thing to preserve that the field source describes, in a form a script can check.
- **Cost:** a first mapping pass per money flow, done by a person with an agent, like the
  surface; upkeep on every money-lane change, carried by the note; one end-to-end test per entry,
  slower than unit tests and needing the test database and the renderers; the first resolver run
  will report many transaction-tier files as unmapped, and each needs a hop or a reason.
- **Follow-ups:** map kvart's invoice total, per-unit charge and payment status, then measure the
  map on the next money-lane ticket (owner: the operator); the resolver with planted true and false
  cases, rehearsed in the blocked direction by replaying cycle 2's poller removal against the map
  (owner: the operator); an assist that proposes hop rows from the orientation map for a person to
  accept (owner: the tool's maintainer).

## Alternatives considered

- **Tiering alone, the status quo:** says which code is money, not which hop closes which state.
  Cycle 2's poller was on the surface and was still scoped out. Rejected.
- **Derive the paths from the call graph:** scheduled jobs, database hand-offs, renderers and
  outbound files cross boundaries a static call graph does not follow, and the poller had no
  caller in the web UI at all. Kept as an assist that proposes rows; a person accepts them.
- **A map per change, inside the note only:** rebuilt each time, uncheckable between changes, gone
  when the ticket closes. The standing map plus the per-change delta in the note keeps both.
- **Paths inside the specs:** a spec is per feature, and a figure crosses features (billing
  computes it, payments advance it, exports render it). Rejected; a spec cites the entry id.
- **Parity replay instead:** needs an oracle, which a greenfield product does not have. The
  agreement test is the oracle-free check; parity replay ([11-scaling](../docs/11-scaling.md) L2)
  stays the stronger rung where an oracle exists.
- **Agreement between exits, no expected value:** catches a hop that diverges, not a figure wrong
  at its source. Rejected; the hand-computed value is part of the test.

## Evidence

- [evidence/kvart-dogfood-cycle-2.md](../evidence/kvart-dogfood-cycle-2.md): the poller HIGH
  `[measured 2026-09-07]`.
- [docs/09-legacy-adoption.md](../docs/09-legacy-adoption.md) §2 and §d: the 20-extractor target,
  68 of 68 mutants, and tiering per class `[measured 2026-09-04]`.
- [evidence/field-evidence.md](../evidence/field-evidence.md) §8: the field source and its caveats.
