<!--
  FEATURE SPEC. Written by the person holding the product or architecture hat, read by
  the fleet that builds the feature. The human approves this file, not the diff: every
  field below is either machine-checkable or names who owns the judgement.
  One file per feature, committed next to the code or in the team context repository.
  If a field cannot be filled, the feature is not ready to build.
-->

# Feature spec: <name>

```yaml
outcome:
  # One sentence describing what is true when this is done, in the user's terms.
  # If it needs two sentences, it is two features.
  <what is true when done>

modules:
  # The target modules this feature may change, taken from the repository's module map.
  # Lanes must be disjoint: two agents working the same module at the same time is the
  # merge conflict you will pay for later.
  - <module>
  - <module>

money_critical: <true|false>
  # True when the change can move money, change what a person is charged, or alter an
  # accounting record. True raises the bar: human sign-off before merge, and mutation
  # testing on the changed money path rather than line coverage alone.

constraints:
  # The surface allowlist (paths, services, APIs that may be touched; everything unlisted
  # is denied), the invariants that must not break, and any performance or capacity budget
  # as a number with units.
  surface: [<path>, <service>]
  invariants:
    - <invariant, and the check that proves it>
  budget: <number with units, or none>

acceptance:
  # Machine-checkable proof that the outcome holds: named tests, queries, or telemetry.
  # Each entry names the command that runs it. "Reviewed and looks right" is not
  # acceptance; it is an opinion with no rerun.
  - id: AC-1
    check: <command or test name>
    proves: <which ticket example this satisfies>
  - id: AC-2
    check: <command or test name>
    proves: <...>

domain_refs:
  # Links into the domain model this feature relies on: the definitions, rules and units
  # whose meaning the code assumes. A feature that invents its own vocabulary instead of
  # citing the model is how two subsystems end up disagreeing about the same word.
  - <path or identifier>

learn_writeback:
  # What this turn adds back to the shared plane once it lands: a new fence in the
  # verification net, a correction to the domain model, a reusable pattern, a memory claim
  # that a cold-start agent would need. Empty here means the loop learned nothing, which
  # is a finding about the process.
  net: <fence added, or none>
  domain_model: <correction, or none>
  pattern: <pattern extracted, or none>
  memory: <claim to write or supersede, or none>
```
