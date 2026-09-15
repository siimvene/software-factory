# Bookstore team context

We build the group's online bookstore: the storefront customers buy from and the
catalog service behind it.

## What we own

- Storefront: the customer-facing web shop (browsing, cart, checkout)
- Catalog: the service holding titles, prices, and stock levels
- Order flow: everything between "pay" and "the warehouse ships it"

## Code repositories

- Piletilevi/bookstore-nuxt-ui (storefront)
- Piletilevi/bookstore-boot-backend (catalog + order flow)
- Piletilevi/bookstore-e2e-tests

## Where things live

- Current-state specs: `specs/` in this repo (generated, never hand-edited; see README)
- Decisions: `docs/adr/` in this repo
- Test environment: https://bookstore-test.example.internal
- Dashboards: https://grafana.example.internal/d/bookstore
- API contract: `bookstore-contract` repo is the source of truth; backend and UI both generate from it

## Domain vocabulary

- Reservation: stock held for a cart, expires after 20 minutes; NOT an order
- Backorder: a sold title with zero stock; ships when restocked, never auto-cancelled
- Bundle: multiple titles sold under one price; one order line, multiple stock movements

## Cross-repo rules

- Money amounts are integer cents everywhere; floats in a price path fail review
- Stock is only ever changed through the catalog service API, never by direct DB write
- Every customer-visible string goes through the translation layer; no hardcoded text
- Refunds are handled by credit, never a reversal API

<!--
This is a filled-in example of the CLAUDE.md template for a fictional team.
Copy CLAUDE.md (the bracketed template), not this file, and keep yours as short.
-->
