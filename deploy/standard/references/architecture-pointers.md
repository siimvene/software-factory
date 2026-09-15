<!-- class: referenced — pointers only, never copied -->

# Architecture Standards (pointers)

Group architecture decisions agents must consult before touching the areas
they govern. All live in Confluence → GAT (Group Architecture and Technologies):

- **Cross-cluster communication using Kafka** (page 2905866249) — services talk
  only to their own cluster's Kafka; cross-cluster flow goes through mirroring;
  mirrored topics carry country-code suffixes. Read before adding any topic,
  producer, or consumer that crosses a cluster boundary.
- **Test environments organization** (page 2855895041) — country-level: one
  staging per country + one develop env per team; group-level: one staging per
  team, develop optional. Read before wiring CI to environments.
- **Architecture birds eye overview** (page 2542895111) — how Portal, Ticketing
  System and GDS fit together; the map for any cross-system task.
