"""
Northlane Connector API — minimal webhook handling example.

Illustrative only: shows the shape of event payloads and a simple
dispatcher pattern. Not wired up to any real web framework.
"""

import hashlib
import hmac

SUPPORTED_EVENTS = [
    "reservation.created",
    "reservation.cancelled",
    "reservation.no_show",
    "resource.state_changed",
]


def verify_signature(payload_bytes, signature_header, webhook_secret):
    """Recompute the HMAC signature and compare against the header.

    Northlane signs webhook bodies with HMAC-SHA256 using the
    per-enterprise webhook secret configured in the dashboard.
    """
    expected = hmac.new(
        webhook_secret.encode("utf-8"), payload_bytes, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature_header)


class WebhookDispatcher:
    """Very small event dispatcher keyed by event type."""

    def __init__(self):
        self._handlers = {}

    def on(self, event_type):
        if event_type not in SUPPORTED_EVENTS:
            raise ValueError(f"Unsupported event type: {event_type}")

        def decorator(fn):
            self._handlers[event_type] = fn
            return fn

        return decorator

    def dispatch(self, event):
        event_type = event.get("type")
        handler = self._handlers.get(event_type)
        if handler is None:
            return None
        return handler(event.get("data", {}))


if __name__ == "__main__":
    dispatcher = WebhookDispatcher()

    @dispatcher.on("reservation.no_show")
    def handle_no_show(data):
        print("Reservation marked as no-show:", data.get("id"))

    example_event = {
        "type": "reservation.no_show",
        "data": {"id": "res_789", "enterprise_id": "ent_123"},
    }
    dispatcher.dispatch(example_event)
