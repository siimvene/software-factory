---
pack: common
description: Example pack. CI gates an agent must not weaken: tests always run, no long-lived keys, branch images never reach production, promotion gates are human decisions
maintainer: the platform owner
status: adopted
source: your organisation's CI/CD standard
---

# CI gates (example pack)

Rules for any agent touching CI workflows, Dockerfiles or deployment configuration.

1. **The test step runs and its failure fails the pipeline.** Never skip, mute or
   conditionally bypass it to get an artifact out.
2. **No long-lived credentials in a workflow.** Registry and cloud auth use workload
   identity federation (or the platform's equivalent). Never add a service-account key file.
3. **One application per repository, one image per build.** Behaviour that differs by market
   or tenant is a feature flag, never a separate build.
4. **Branch builds are for test environments only.** An image built from a feature branch is
   never promoted to production.
5. **Tagging is an organisation convention.** Do not switch a repository's tag scheme ad
   hoc; deploy automation sorts and filters on it.
6. **Promotion gates are architecture, not task work.** An agent must not weaken a promotion
   gate, switch a repository between promotion styles, or add production image automation.
   Surface the change in the PR for a human decision.
