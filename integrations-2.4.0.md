# Integrating Northlane with external systems

> **API version:** 2.4.0 (2026-06-15)

This document describes how the Northlane Connector API is designed to be integrated into a broader software stack — POS systems, payment processors, CRMs, accounting platforms, revenue management tools, and similar. It covers the integration surface **Northlane exposes**: authentication, data exchange patterns, and event delivery.

It does not document the internals, APIs, or configuration of any specific third-party product. If you're connecting Northlane to another platform, consult that platform's own documentation for how it consumes external data; this doc only covers what Northlane sends, receives, and expects.

## Contents

- [Integration patterns](#integration-patterns)
- [Pull-based integration](#pull-based-integration)
- [Push-based integration (webhooks)](#push-based-integration-webhooks)
- [Bidirectional sync](#bidirectional-sync)
- [Scoped access for third-party integrations](#scoped-access-for-third-party-integrations)
- [Data mapping considerations](#data-mapping-considerations)
- [Common integration categories](#common-integration-categories)
- [Reliability and error handling](#reliability-and-error-handling)

## Integration patterns

Most integrations with Northlane follow one of three shapes:

| Pattern | Description | Typical use |
|---|---|---|
| **Pull** | The external system periodically calls Northlane's REST endpoints to read current state | Reporting tools, BI dashboards, nightly syncs |
| **Push** | Northlane sends webhook events to the external system as they happen | Real-time notifications, messaging tools, automation |
| **Bidirectional** | Both sides read and write, usually with Northlane as the system of record for reservations/resources | POS, channel managers, payment flows |

Which pattern fits depends on how time-sensitive the data is and whether the external system needs to write back into Northlane, not just read from it.

## Pull-based integration

External systems can query current state at any time using the standard REST endpoints described in [concepts.md](concepts.md) (`GET /v1/enterprises/{id}/resources`, `GET /v1/reservations`, etc). This is the simplest integration shape and requires no persistent connection.

Pull integrations should:

- Use a token scoped only to what they need (see [Scoped access](#scoped-access-for-third-party-integrations) below)
- Respect the rate limits described in [concepts.md](concepts.md#rate-limits)
- Prefer incremental queries (filtering by `updated_since`) over full re-fetches where the endpoint supports it, to avoid unnecessary load on both sides

Pull is a reasonable default when the integration only needs to *read* from Northlane and near-real-time freshness isn't critical (e.g. nightly exports to an accounting system).

## Push-based integration (webhooks)

For integrations that need to react to changes as they happen, Northlane can push events to a registered webhook endpoint. Supported event types are listed in [`connector/webhooks.py`](../connector/webhooks.py) (`SUPPORTED_EVENTS`) and include reservation lifecycle events (`reservation.created`, `reservation.cancelled`, `reservation.no_show`) and resource state changes (`resource.state_changed`).

Key properties of Northlane's webhook delivery:

- Payloads are signed with HMAC-SHA256 using a per-enterprise secret; recipients should verify the signature before trusting a payload (see `verify_signature()` in `webhooks.py`)
- Delivery is at-least-once — a receiving system should treat duplicate deliveries of the same event ID as a no-op, not an error
- The `webhooks:manage` scope is required to register or modify webhook subscriptions
- Registering a webhook is done via the dashboard or `POST /v1/webhooks`, specifying a target URL and the subset of event types to subscribe to

Push is the right shape when the external system needs to react quickly — for example, triggering a guest message, unlocking a door, or updating a POS folio the moment a reservation is confirmed.

## Bidirectional sync

Some integrations need to both read from and write to Northlane — for example, a system that manages its own booking calendar but also needs Northlane to reflect reservations made elsewhere. In these cases:

- Northlane should generally be treated as the **system of record** for reservation and resource state, to avoid conflicting writes from multiple sources
- Writes from external systems should always include an `Idempotency-Key` (see [concepts.md](concepts.md#idempotency)) so retried writes don't create duplicate reservations
- Where two systems can each independently change the same resource, integrators should design for eventual consistency and use webhook events to reconcile state rather than assuming both sides are always in sync

Northlane does not currently support field-level conflict resolution — the most recent write via the API wins. Integrators building bidirectional sync should account for this at the application layer.

## Scoped access for third-party integrations

When connecting a third-party system to Northlane, issue it a token scoped to only what it needs, rather than reusing a broad `owner`-level token. This limits blast radius if the third-party system's credentials are ever compromised, and makes the audit log (`actor_role` on each event) more meaningful.

Some illustrative (not exhaustive) scope combinations for common integration shapes:

| Integration shape | Suggested scopes |
|---|---|
| Read-only reporting/BI export | `reports:read` |
| Availability sync (read-only) | `resources:read` |
| Reservation creation from an external booking source | `reservations:read`, `reservations:write` |
| Resource state sync (e.g. maintenance/IoT systems) | `resources:read`, `resources:write` |
| Event-driven automation (no direct API writes) | `webhooks:manage` only |

As of 2.4.0, there is no dedicated scope for invoice or payment data — integrations needing that information require an `owner`-level token. A narrower, purpose-built scope for this is on the roadmap.

See [authentication.md](authentication.md) for the full scope list and how scopes map to Northlane's built-in roles.

## Data mapping considerations

Northlane's object model (enterprises, resources, reservations) is intentionally generic so it can represent hotel rooms, desks, tables, or equipment slots under one schema. When integrating with a system that has its own, more specific data model, expect to do some translation on your end:

- Northlane's `resource_category` is a free-text field on Northlane's side — external systems with a fixed set of resource types will need their own mapping table between their types and Northlane's categories
- `attributes` on a resource is a free-form key/value map; there is no fixed schema, so integrators should treat unknown keys as forward-compatible rather than erroring on them
- Pricing units (`night`, `hour`, `slot`) may not correspond 1:1 to time or pricing concepts in every external system — see [concepts.md](concepts.md#time-units)

Northlane does not attempt to normalize these to any external standard; that mapping is the integrator's responsibility.

## Common integration categories

The following are common categories of systems that integrate with Northlane, described only in terms of what they typically need from Northlane's API surface — not how those systems work internally:

- **Property/booking-adjacent systems** (e.g. channel managers) — typically bidirectional, syncing reservations and availability
- **Point-of-sale systems** — typically push-consuming (reservation events) plus pull for resource/guest lookups
- **Payment and billing systems** — typically consumers of reservation and reporting endpoints; as of 2.4.0 this requires an `owner`-level token, since no narrower billing-specific scope exists yet
- **CRM and guest messaging tools** — typically push-consuming reservation lifecycle events
- **Accounting/ERP systems** — typically pull-based, often on a scheduled batch basis
- **Business intelligence tools** — typically pull-based, read-only, using `reports:read`
- **IoT and access-control systems** — typically push-consuming `resource.state_changed` and reservation events
- **Identity providers** — integrate at the dashboard/account level for user authentication, separate from the API token model described above

For guidance on any specific platform in these categories, refer to that platform's own integration or developer documentation — Northlane's docs only describe our side of the interface.

## Reliability and error handling

Integrators should design for the following, regardless of which pattern they use:

- Webhook delivery failures are retried on a backoff schedule; a receiving endpoint that is down briefly will still eventually receive the event, but should not assume ordering is preserved across retries
- Pull requests that hit a rate limit should back off using the `Retry-After` header rather than retrying immediately
- All state-changing requests should be idempotent on the integrator's side, using `Idempotency-Key`, since network failures can leave the success/failure of a request ambiguous

Northlane's guarantees stop at its own API boundary. What an external system does with the data it receives — retries, storage, further downstream integration — is outside the scope of this document.
