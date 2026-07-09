# Concepts

This section covers the domain-specific concepts used throughout the Northlane Connector API. Understanding these will help you integrate more effectively.

> **Terminology note:** Some terms below are used in a specific way inside Northlane. For example, we use *enterprise* to describe a single managed property or business unit, and *resource* to describe any bookable unit (a room, desk, table, or equipment slot). See the [Glossary](glossary.md) if a term is unfamiliar — note that this example repo does not include a glossary file.

## Contents

- [Enterprises & Portfolios](#enterprises--portfolios)
- [Resources](#resources)
- [Access Tokens & Scopes](#access-tokens--scopes)
- [Rate Limits](#rate-limits)
- [Idempotency](#idempotency)
- [Time Units](#time-units)

---

## Enterprises & Portfolios

An **enterprise** is the top-level object representing a single managed business (a hotel, a coworking site, a clinic, etc). Enterprises can be grouped into a **portfolio** for chains or franchises that operate multiple locations under one account.

A **Portfolio Access Token (PAT)** grants access across every enterprise in a portfolio, whereas a standard **Enterprise Token** is scoped to a single enterprise. Most integrations should request the narrowest token that satisfies their use case.

## Resources

A **resource** is anything that can be reserved: a hotel room, a meeting room, a piece of equipment, a restaurant table. Resources belong to a **resource category** (e.g. `room`, `desk`, `table`) and carry:

- `capacity` — maximum occupancy or usage count
- `state` — one of `available`, `held`, `occupied`, `out-of-service`
- `attributes` — a free-form key/value map for category-specific data (e.g. `floor`, `view`, `accessible`)

## Access Tokens & Scopes

Every request must include an `Authorization` header with a bearer token. Tokens are issued per enterprise (or per portfolio, for PATs) and carry one or more **scopes**:

| Scope | Grants |
|---|---|
| `reservations:read` | Read-only access to reservation data |
| `reservations:write` | Create, modify, cancel reservations |
| `resources:read` | Read-only access to resource inventory |
| `resources:write` | Update resource state and attributes |
| `webhooks:manage` | Register and manage webhook subscriptions |
| `reports:read` | Access to aggregated reporting endpoints |

See [authentication.md](authentication.md) for how scopes map onto user roles.

## Rate Limits

The Connector API enforces a rolling rate limit per token:

- **600 requests / minute** for standard Enterprise Tokens
- **2,400 requests / minute** for Portfolio Access Tokens
- Burst allowance of 50 requests in any 1-second window

Exceeding the limit returns `HTTP 429` with a `Retry-After` header (seconds).

## Idempotency

State-changing requests (`POST`, `PUT`, `PATCH`) accept an `Idempotency-Key` header. Replaying the same key within 24 hours returns the original response instead of re-processing the request. This is the recommended way to safely retry on network failure.

## Time Units

Reservation durations are expressed in **service time units (STUs)**, not raw hours, because some resource categories (e.g. daily hotel rooms vs. hourly desks) use different granularity. See `resources.pricing_unit` on the resource object to determine whether a given resource is billed in `night`, `hour`, or `slot` units.
