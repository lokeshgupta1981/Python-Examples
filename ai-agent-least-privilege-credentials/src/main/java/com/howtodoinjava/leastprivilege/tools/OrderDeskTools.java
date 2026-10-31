package com.howtodoinjava.leastprivilege.tools;

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;

import org.springframework.ai.chat.model.ToolContext;
import org.springframework.ai.tool.annotation.Tool;
import org.springframework.ai.tool.annotation.ToolParam;

import com.howtodoinjava.leastprivilege.db.DbCredential;

/**
 * The three OrderDesk tools. Each one gets its credential from its own source;
 * none of them sees another tool's credential, and the model sees none at all.
 */
public class OrderDeskTools {

    private final String jdbcUrl;
    private final DatabaseCredentials database;
    private final OrdersTokens ordersTokens;
    private final ReportsTokens reportsTokens;
    private final String ordersApi;
    private final String reportsApi;
    private final HttpClient http = HttpClient.newHttpClient();

    public OrderDeskTools(String jdbcUrl, DatabaseCredentials database, OrdersTokens ordersTokens,
                          ReportsTokens reportsTokens, String ordersApi, String reportsApi) {
        this.jdbcUrl = jdbcUrl;
        this.database = database;
        this.ordersTokens = ordersTokens;
        this.reportsTokens = reportsTokens;
        this.ordersApi = ordersApi;
        this.reportsApi = reportsApi;
    }

    @Tool(description = "List the signed-in customer's orders with id, item, total and status.")
    public String findOrders(ToolContext context) {
        String customerId = (String) context.getContext().get("customerId");
        DbCredential login = database.current();
        try (Connection c = DriverManager.getConnection(jdbcUrl, login.username(), login.password());
             PreparedStatement ps = c.prepareStatement(
                     "SELECT id, item, total, status FROM orders WHERE customer_id = ? ORDER BY id")) {
            ps.setString(1, customerId);
            List<String> rows = new ArrayList<>();
            try (ResultSet rs = ps.executeQuery()) {
                while (rs.next()) {
                    rows.add(rs.getString(1) + ": " + rs.getString(2) + ", " + rs.getBigDecimal(3)
                            + " USD, " + rs.getString(4));
                }
            }
            return rows.isEmpty() ? "No orders." : String.join("\n", rows);
        } catch (SQLException e) {
            throw new IllegalStateException("findOrders failed on " + jdbcUrl, e);
        }
    }

    @Tool(description = "Cancel one of the signed-in customer's orders by its id, for example A-1002.")
    public String cancelOrder(@ToolParam(description = "Order id") String orderId, ToolContext context) {
        String userToken = (String) context.getContext().get("userAccessToken");
        HttpResponse<String> response = post(ordersApi + "/orders/" + orderId + "/cancel",
                ordersTokens.tokenFor(userToken), "");
        return switch (response.statusCode()) {
            case 200 -> "Order " + orderId + " is cancelled.";
            case 403 -> "Not allowed: order " + orderId + " can't be cancelled for this customer.";
            case 404 -> "There is no order " + orderId + ".";
            default -> "The Orders API answered " + response.statusCode() + ".";
        };
    }

    @Tool(description = "Add a one-sentence summary of this conversation to the support team's daily report.")
    public String sendReport(@ToolParam(description = "One-sentence summary") String summary) {
        HttpResponse<String> response = post(reportsApi + "/reports", reportsTokens.token(), summary);
        return response.statusCode() == 202 ? "Report queued." : "The Reports API answered " + response.statusCode() + ".";
    }

    private HttpResponse<String> post(String url, String token, String body) {
        HttpRequest request = HttpRequest.newBuilder(URI.create(url))
                .header("Authorization", "Bearer " + token)
                .POST(HttpRequest.BodyPublishers.ofString(body))
                .build();
        try {
            return http.send(request, HttpResponse.BodyHandlers.ofString());
        } catch (IOException e) {
            throw new IllegalStateException("Call to " + url + " failed", e);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new IllegalStateException(e);
        }
    }
}
