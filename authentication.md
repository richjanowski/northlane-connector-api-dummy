# Authentication & Roles

This document explains how authentication works in the Northlane Connector API and how internal user roles map to API scopes.

## Contents

- [Token Types](#token-types)
- [Requesting a Token](#requesting-a-token)
- [User Roles](#user-roles)
- [Role-to-Scope Mapping](#role-to-scope-mapping)
- [Revocation](#revocation)

## Token Types

| Token type | Scope of access | Typical consumer |
|---|---|---|
| Enterprise Token | Single enterprise | Property-level integrations (channel managers, POS) |
| Portfolio Access Token (PAT) | All enterprises in a portfolio | Chain-level dashboards, BI tools |
| Service Token | System-to-system, no user attached | Internal automation, scheduled jobs |

## Requesting a Token

```
POST /v1/oauth/token
Content-Type: application/json

{
  "grant_type": "client_credentials",
  "client_id": "your-client-id",
  "client_secret": "your-client-secret",
  "scope": "reservations:read resources:read"
}
```

A successful response returns an access token valid for 3600 seconds. Tokens should be refreshed proactively rather than waiting for a `401`.

## User Roles

Northlane's dashboard defines six built-in roles. These are relevant to integrators because webhook payloads and audit log entries include the `actor_role` of whoever triggered a change.

| Role | Description |
|---|---|
| `owner` | Full access to all enterprises in the portfolio, billing, and user management |
| `billing_admin` | Invoice access and payment method management for a single enterprise, without full `owner` rights. Added in 2.5.0. |
| `manager` | Full operational access to a single enterprise; cannot manage billing |
| `front_desk` | Can create/modify reservations and update resource state |
| `housekeeping` | Can update resource state (`available`, `out-of-service`) only |
| `reporting_viewer` | Read-only access to reports and reservation history |

## Role-to-Scope Mapping

| Role | Default scopes |
|---|---|
| `owner` | `reservations:read`, `reservations:write`, `resources:read`, `resources:write`, `webhooks:manage`, `reports:read`, `billing:manage` |
| `billing_admin` | `billing:manage`, `reports:read` |
| `manager` | `reservations:read`, `reservations:write`, `resources:read`, `resources:write`, `reports:read` |
| `front_desk` | `reservations:read`, `reservations:write`, `resources:read` |
| `housekeeping` | `resources:read`, `resources:write` |
| `reporting_viewer` | `reservations:read`, `reports:read` |

> **Note on 2.5.0:** billing access used to be an implicit part of `owner` with no dedicated scope. As of 2.5.0, it's gated behind the explicit `billing:manage` scope, and can now be delegated independently via the new `billing_admin` role.

This mapping is also available programmatically — see [`config/roles.json`](../config/roles.json) in this repo for the machine-readable version used by the dashboard's permission checks.

## Revocation

Tokens can be revoked immediately via `DELETE /v1/oauth/token/{token_id}`, or will expire naturally after 1 hour. Revoking a user's dashboard access automatically revokes any tokens issued under that user's identity within 60 seconds.
