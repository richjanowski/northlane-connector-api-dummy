# Changelog

All notable changes to the Northlane Connector API are documented here. Format loosely follows [Keep a Changelog](https://keepachangelog.com/).

## [2.5.0] - 2026-07-01

### Added
- New `billing:manage` scope, covering invoice access and payment method updates.
- New built-in role `billing_admin`, scoped to a single enterprise, for teams that want billing access without full `owner` rights.
- `reservations.waitlist` feature: resources at capacity can now accept waitlisted reservations via `POST /v1/reservations/waitlist`. Available on Growth and Enterprise plans.

### Changed
- Rate limit for standard Enterprise Tokens raised from 600 to 900 requests/minute.
- `owner` role's default scopes now explicitly include `billing:manage` (previously billing access was implicit and not scope-gated).

### Deprecated
- The `reports:read`-only combination for billing summaries (`GET /v1/enterprises/{id}/reports/billing`) is deprecated in favor of the new `billing:manage`-gated `GET /v1/enterprises/{id}/billing/invoices`. Will be removed in 3.0.0.

---

## [2.4.0] - 2026-06-15

### Added
- New `resources:write` scope now supports bulk state updates via `PATCH /v1/resources/bulk`.
- `reporting_viewer` role added as a new built-in role (previously reporting access required `manager`).
- Webhook event `reservation.no_show` added.

### Changed
- Rate limit for Portfolio Access Tokens raised from 1,200 to 2,400 requests/minute.
- `Idempotency-Key` header is now required (previously optional) on all `POST /v1/reservations` calls.

### Fixed
- Fixed an issue where `resource.attributes` could return stale values for up to 30 seconds after an update.

---

## [2.3.1] - 2026-04-02

### Fixed
- Corrected `Retry-After` header units (was returning milliseconds, now correctly returns seconds).
- Fixed webhook signature verification failing for payloads over 64KB.

---

## [2.3.0] - 2026-02-20

### Added
- Support for `slot`-based pricing units, in addition to existing `night` and `hour` units.
- New endpoint `GET /v1/enterprises/{id}/resources/availability` for real-time availability queries.

### Deprecated
- `GET /v1/availability` (enterprise-scoped, non-resource-specific) is deprecated in favor of the endpoint above. Will be removed in 3.0.0.

---

## [2.2.0] - 2025-11-08

### Added
- Introduced Portfolio Access Tokens (PATs) for multi-enterprise chains.
- `webhooks:manage` scope split out from `reservations:write` (previously bundled together).

### Security
- Tokens issued to a dashboard user are now revoked within 60 seconds of that user's access being removed, down from a previous best-effort window of up to 15 minutes.

---

## [2.1.0] - 2025-08-30

### Added
- Initial public release of the Connector API, covering `reservations`, `resources`, and basic webhook support.
