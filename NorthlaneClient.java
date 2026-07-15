/**
 * Northlane Connector API — minimal example client.
 *
 * This is a lightweight illustrative stub, not a production client.
 * It mirrors the shape of the Python example client (see connector/client.py).
 */

import java.util.HashMap;
import java.util.Map;

public class NorthlaneClient {

    private static final String DEFAULT_BASE_URL = "https://api.northlane.example/v1";
    private static final long TOKEN_TTL_SECONDS = 3600;

    private final String clientId;
    private final String clientSecret;
    private final String baseUrl;

    private String accessToken;
    private long tokenExpiresAt;

    public NorthlaneClient(String clientId, String clientSecret) {
        this(clientId, clientSecret, DEFAULT_BASE_URL);
    }

    public NorthlaneClient(String clientId, String clientSecret, String baseUrl) {
        this.clientId = clientId;
        this.clientSecret = clientSecret;
        this.baseUrl = baseUrl;
    }

    /**
     * Fetch (or reuse) an access token for the given scopes.
     * In a real client this would POST to /oauth/token. Here we simulate
     * issuing a token so the example is runnable without a network call.
     */
    public String authenticate(String[] scopes) {
        long now = System.currentTimeMillis() / 1000;
        if (accessToken != null && now < tokenExpiresAt) {
            return accessToken;
        }

        StringBuilder joined = new StringBuilder();
        for (String scope : scopes) {
            if (joined.length() > 0) {
                joined.append("-");
            }
            joined.append(scope);
        }

        this.accessToken = "example-token-" + joined;
        this.tokenExpiresAt = now + TOKEN_TTL_SECONDS;
        return this.accessToken;
    }

    /**
     * Return a placeholder resource object.
     * Real implementation would call:
     * GET {baseUrl}/enterprises/{enterpriseId}/resources/{resourceId}
     */
    public Map<String, Object> getResource(String enterpriseId, String resourceId) {
        Map<String, Object> resource = new HashMap<>();
        resource.put("id", resourceId);
        resource.put("enterprise_id", enterpriseId);
        resource.put("category", "room");
        resource.put("state", "available");

        Map<String, Object> attributes = new HashMap<>();
        attributes.put("floor", 3);
        attributes.put("view", "courtyard");
        resource.put("attributes", attributes);

        return resource;
    }

    /**
     * Return a placeholder reservation object.
     * Real implementation would POST to /v1/reservations with an
     * Idempotency-Key header.
     */
    public Map<String, Object> createReservation(String enterpriseId, String resourceId,
            String start, String end, String idempotencyKey) {
        if (idempotencyKey == null || idempotencyKey.isEmpty()) {
            throw new IllegalArgumentException("idempotencyKey is required for reservation creation");
        }

        Map<String, Object> reservation = new HashMap<>();
        reservation.put("id", "res_" + idempotencyKey.substring(0, Math.min(8, idempotencyKey.length())));
        reservation.put("enterprise_id", enterpriseId);
        reservation.put("resource_id", resourceId);
        reservation.put("start", start);
        reservation.put("end", end);
        reservation.put("status", "confirmed");

        return reservation;
    }

    public static void main(String[] args) {
        NorthlaneClient client = new NorthlaneClient("demo", "demo-secret");

        String token = client.authenticate(new String[] {"resources:read"});
        System.out.println("Issued token: " + token);

        Map<String, Object> resource = client.getResource("ent_123", "res_456");
        System.out.println("Resource: " + resource);
    }
}
