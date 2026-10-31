package com.howtodoinjava.leastprivilege.api;

import java.io.IOException;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.CopyOnWriteArrayList;

import com.howtodoinjava.leastprivilege.auth.BearerTokenValidator;
import com.howtodoinjava.leastprivilege.db.OrderDeskDatabase;
import com.nimbusds.jwt.JWTClaimsSet;
import com.sun.net.httpserver.HttpExchange;

/**
 * POST /orders/{id}/cancel. Needs a token for audience "orders-api" with scope
 * "orders:cancel". A token issued for a user may cancel only that user's orders.
 */
public class OrdersApi extends ProtectedApi {

    public static final String AUDIENCE = "orders-api";

    /** One line per cancellation: who the order belonged to, who asked, and through which client. */
    public record Cancellation(String orderId, String subject, String actor) {
    }

    private final OrderDeskDatabase database;
    private final List<Cancellation> cancellations = new CopyOnWriteArrayList<>();

    public OrdersApi(BearerTokenValidator validator, OrderDeskDatabase database) {
        super(validator, "/orders/");
        this.database = database;
    }

    @Override
    void handle(HttpExchange exchange, JWTClaimsSet claims) throws IOException {
        String[] parts = exchange.getRequestURI().getPath().split("/");
        if (parts.length != 4 || !"cancel".equals(parts[3]) || !"POST".equals(exchange.getRequestMethod())) {
            send(exchange, 404, Map.of("error", "not_found"));
            return;
        }
        if (!hasScope(claims, "orders:cancel")) {
            insufficientScope(exchange, "orders:cancel");
            return;
        }
        String orderId = parts[2];
        try (Connection c = database.ownerConnection()) {
            String owner = ownerOf(c, orderId);
            if (owner == null) {
                send(exchange, 404, Map.of("error", "not_found"));
                return;
            }
            boolean serviceToken = claims.getSubject().equals(claims.getClaim("client_id"));
            if (!serviceToken && !owner.equals(claims.getSubject())) {
                send(exchange, 403, Map.of("error", "forbidden", "reason", "order belongs to another customer"));
                return;
            }
            try (PreparedStatement update = c.prepareStatement("UPDATE orders SET status = 'CANCELLED' WHERE id = ?")) {
                update.setString(1, orderId);
                update.executeUpdate();
            }
        } catch (SQLException e) {
            send(exchange, 500, Map.of("error", "server_error"));
            return;
        }
        Object act = claims.getClaim("act");
        String actor = act instanceof Map<?, ?> m ? String.valueOf(m.get("sub")) : "-";
        cancellations.add(new Cancellation(orderId, claims.getSubject(), actor));
        Map<String, Object> body = new LinkedHashMap<>();
        body.put("order", orderId);
        body.put("status", "CANCELLED");
        send(exchange, 200, body);
    }

    private static String ownerOf(Connection c, String orderId) throws SQLException {
        try (PreparedStatement ps = c.prepareStatement("SELECT customer_id FROM orders WHERE id = ?")) {
            ps.setString(1, orderId);
            try (ResultSet rs = ps.executeQuery()) {
                return rs.next() ? rs.getString(1) : null;
            }
        }
    }

    public List<Cancellation> cancellations() {
        return List.copyOf(cancellations);
    }
}
