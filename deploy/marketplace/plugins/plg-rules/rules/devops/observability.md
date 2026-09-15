---
pack: devops
description: PLG observability rules — OpenTelemetry-only telemetry, structured JSON logs, required resource attributes, service onboarding checklist
maintainer: TBD
status: adopted
source: Confluence GPM "Observability Standard — Piletilevi Infrastructure" (page 2640969741, Feb 2026, adopted 2026-07-22)
---

# Observability Rules

Sources of truth: Confluence → GPM → *Observability Standard — Piletilevi
Infrastructure* (mandatory, staging + production, Baltic infra) and GAT →
*Monitoring solutions policy* (status: proposal). These rules are the
developer-facing projection; consult the full standards for collector/infra
detail.

## Scope: which stack applies

- **Baltic infra (Nomad/Docker, DevOps-run Grafana stack):** the rules below
  are mandatory in full. OpenTelemetry is required for new projects.
- **GCP deployments:** Google Cloud Logging/APM is the accepted default;
  routing through an OTel Collector is recommended where it has no significant
  downside (keeps a future stack switch possible). The JSON-structured-logs
  rule applies everywhere.
- **DataDog and Honeycomb are being phased out** — never introduce them into
  new work.

## Hard requirements (Baltic infra)

1. **OpenTelemetry is the only permitted telemetry agent.** Do not add
   Prometheus exporters, Filebeat, Logstash shippers, or any agent outside the
   OTel stack to a service or host.
2. **All application logs are structured JSON.** Plain-text logs are not
   parsed — they land as raw strings with no level/field extraction.
3. Telemetry configuration is Infrastructure as Code (Ansible). Never configure
   Grafana dashboards or alerts manually in any environment.

## Service integration

- OTLP endpoints: `otel-gw:4317` (gRPC) / `otel-gw:4318` (HTTP).
- Container stdout/stderr is collected automatically by Fluent Bit — do not
  add a log shipper for container logs.
- `OTEL_SERVICE_NAME` is required on every service: unique, lowercase,
  kebab-case (e.g. `ticket-control`), plus the standard resource attributes
  from the full standard.
- Browser apps (staging only): Grafana Faro SDK → `http://otel-gw:12347`.

## Onboarding checklist (new service)

1. Add the OpenTelemetry SDK for the service's language.
2. Set `OTEL_SERVICE_NAME` + required resource attributes.
3. Point the OTLP exporter at `otel-gw:4317`/`4318`.
4. Container logs: nothing to do (Fluent Bit).
5. Notify DevOps to register the service name on `otel-gw`.

## Alerting

Alerts are code (Ansible → Grafana Unified Alerting). Severities: `warning`
(degradation) / `critical` (outage or imminent failure). An agent may propose
alert rule changes via PR to the IaC repo; never via the Grafana UI.

## Relationship to the language logging packs

The per-stack logging rules (`backend-java`, `backend-python`,
`frontend-typescript`) govern **log content** — what to log, levels, forbidden
data, audit events. This file governs **transport and format**. Where a
language pack describes a specific shipping mechanism (e.g. Logstash encoder
wiring), this standard wins: JSON structure per the pack, delivery via the
OTel stack.
