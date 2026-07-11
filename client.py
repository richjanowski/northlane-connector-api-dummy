"""
Northlane Connector API — minimal example client.

This is a lightweight illustrative stub, not a production client.
It shows the basic shape of authentication and a couple of common calls.
"""

import time

DEFAULT_BASE_URL = "https://api.northlane.example/v1"
TOKEN_TTL_SECONDS = 3600


class NorthlaneClient:
    """A minimal example client for the Northlane Connector API."""

    def __init__(self, client_id, client_secret, base_url=DEFAULT_BASE_URL):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = base_url
        self._access_token = None
        self._token_expires_at = 0

    def authenticate(self, scopes=None):
        """Fetch (or reuse) an access token for the given scopes.

        In a real client this would POST to /oauth/token. Here we just
        simulate issuing a token so the example is runnable without a
        network call.
        """
        scopes = scopes or ["reservations:read", "resources:read"]
        if self._access_token and time.time() < self._token_expires_at:
            return self._access_token

        self._access_token = "example-token-" + "-".join(scopes)
        self._token_expires_at = time.time() + TOKEN_TTL_SECONDS
        return self._access_token

    def get_resource(self, enterprise_id, resource_id):
        """Return a placeholder resource object.

        Real implementation would call:
        GET {base_url}/enterprises/{enterprise_id}/resources/{resource_id}
        """
        return {
            "id": resource_id,
            "enterprise_id": enterprise_id,
            "category": "room",
            "state": "available",
            "attributes": {"floor": 3, "view": "courtyard"},
        }

    def create_reservation(self, enterprise_id, resource_id, start, end, idempotency_key=None):
        """Return a placeholder reservation object.

        Real implementation would POST to /v1/reservations with an
        Idempotency-Key header.
        """
        if idempotency_key is None:
            raise ValueError("idempotency_key is required for reservation creation")

        return {
            "id": "res_" + idempotency_key[:8],
            "enterprise_id": enterprise_id,
            "resource_id": resource_id,
            "start": start,
            "end": end,
            "status": "confirmed",
        }


if __name__ == "__main__":
    client = NorthlaneClient(client_id="demo", client_secret="demo-secret")
    token = client.authenticate(["resources:read"])
    print("Issued token:", token)

    resource = client.get_resource("ent_123", "res_456")
    print("Resource:", resource)
