/**
 * Northlane Connector API — minimal example webhook listener.
 *
 * Illustrative only: shows how a receiving endpoint might verify and
 * dispatch Northlane webhook events. Not wired up to a real HTTP server.
 * Mirrors connector/webhooks.py.
 */

const crypto = require("crypto");

const SUPPORTED_EVENTS = [
  "reservation.created",
  "reservation.cancelled",
  "reservation.no_show",
  "resource.state_changed",
];

function verifySignature(payloadRaw, signatureHeader, webhookSecret) {
  const expected = crypto
    .createHmac("sha256", webhookSecret)
    .update(payloadRaw)
    .digest("hex");

  return crypto.timingSafeEqual(
    Buffer.from(expected, "utf8"),
    Buffer.from(signatureHeader, "utf8")
  );
}

class WebhookDispatcher {
  constructor() {
    this.handlers = {};
  }

  on(eventType, handler) {
    if (!SUPPORTED_EVENTS.includes(eventType)) {
      throw new Error(`Unsupported event type: ${eventType}`);
    }
    this.handlers[eventType] = handler;
  }

  dispatch(event) {
    const handler = this.handlers[event.type];
    if (!handler) return null;
    return handler(event.data || {});
  }
}

// Example usage
const dispatcher = new WebhookDispatcher();

dispatcher.on("reservation.no_show", (data) => {
  console.log("Reservation marked as no-show:", data.id);
});

const exampleEvent = {
  type: "reservation.no_show",
  data: { id: "res_789", enterprise_id: "ent_123" },
};

dispatcher.dispatch(exampleEvent);

module.exports = { verifySignature, WebhookDispatcher, SUPPORTED_EVENTS };
