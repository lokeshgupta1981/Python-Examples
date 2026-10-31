package com.howtodoinjava.leastprivilege;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.time.Duration;
import java.time.Instant;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.function.Function;

import com.howtodoinjava.leastprivilege.db.DbCredential;
import com.howtodoinjava.leastprivilege.tools.ClientCredentialsTokens;

/**
 * Runs the same attacks against both setups and prints what happened. Each attack
 * uses a credential that one tool really holds, as if an attacker controlled that tool.
 */
public class AttackMatrix {

    private static final HttpClient HTTP = HttpClient.newHttpClient();

    public static void main(String[] args) {
        Map<String, Function<OrderDesk, String>> attacks = new LinkedHashMap<>();
        attacks.put("findOrders login: DROP TABLE orders", d -> sql(d, "DROP TABLE orders"));
        attacks.put("findOrders login: read customer emails", d -> sql(d, "SELECT email FROM customers"));
        attacks.put("findOrders login: reuse it 5 minutes later", AttackMatrix::reuseLoginLater);
        attacks.put("cancelOrder token: cancel C-77's order B-2001", d ->
                post(d.ordersApi.baseUrl() + "/orders/B-2001/cancel", d.cancelOrderTokens.tokenFor(d.signIn("C-42"))));
        attacks.put("cancelOrder token: call the Reports API", d ->
                post(d.reportsApi.baseUrl() + "/reports", d.cancelOrderTokens.tokenFor(d.signIn("C-42"))));
        attacks.put("sendReport token: cancel order A-1001", d ->
                post(d.ordersApi.baseUrl() + "/orders/A-1001/cancel", d.sendReportTokens.token()));
        attacks.put("agent client: get orders:cancel with no user", AttackMatrix::tokenWithoutUser);

        System.out.println("| Attack | One shared key | Scoped credentials |");
        System.out.println("|---|---|---|");
        attacks.forEach((name, attack) -> {
            String shared = run(OrderDesk::sharedKey, attack);
            String scoped = run(OrderDesk::scoped, attack);
            System.out.println("| " + name + " | " + shared + " | " + scoped + " |");
        });
    }

    private static String run(Function<MutableClock, OrderDesk> setup, Function<OrderDesk, String> attack) {
        try (OrderDesk desk = setup.apply(new MutableClock(Instant.now()))) {
            return attack.apply(desk);
        } catch (RuntimeException e) {
            return "Blocked: " + firstLine(e.getMessage());
        }
    }

    private static String sql(OrderDesk desk, String statement) {
        DbCredential login = desk.findOrdersLogin.current();
        try (Connection c = desk.database.connect(login.username(), login.password());
             Statement s = c.createStatement()) {
            if (s.execute(statement)) {
                try (ResultSet rs = s.getResultSet()) {
                    int rows = 0;
                    while (rs.next()) {
                        rows++;
                    }
                    return "Worked: read " + rows + " rows";
                }
            }
            return "Worked";
        } catch (SQLException e) {
            return "Blocked: " + firstLine(e.getMessage());
        }
    }

    private static String reuseLoginLater(OrderDesk desk) {
        DbCredential login = desk.findOrdersLogin.current();
        ((MutableClock) desk.clock).advance(Duration.ofMinutes(5));
        desk.broker.revokeExpired();
        try (Connection c = desk.database.connect(login.username(), login.password())) {
            return "Worked";
        } catch (SQLException e) {
            return "Blocked: " + firstLine(e.getMessage());
        }
    }

    private static String tokenWithoutUser(OrderDesk desk) {
        boolean shared = desk.secrets.get("admin") != null && desk.cancelOrderTokens instanceof ClientCredentialsTokens;
        ClientCredentialsTokens client = shared
                ? new ClientCredentialsTokens(desk.authServer.tokenUri(), "orderdesk-admin", desk.secrets.get("admin"),
                "orders:cancel")
                : new ClientCredentialsTokens(desk.authServer.tokenUri(), OrderDesk.AGENT_CLIENT, desk.secrets.get("agent"),
                "orders:cancel");
        client.token();
        return "Worked";
    }

    private static String post(String url, String token) {
        try {
            HttpResponse<String> response = HTTP.send(HttpRequest.newBuilder(URI.create(url))
                    .header("Authorization", "Bearer " + token)
                    .POST(HttpRequest.BodyPublishers.ofString("attack")).build(), HttpResponse.BodyHandlers.ofString());
            return (response.statusCode() < 300 ? "Worked: " : "Blocked: ") + response.statusCode() + " " + response.body();
        } catch (Exception e) {
            throw new IllegalStateException(e);
        }
    }

    private static String firstLine(String message) {
        return message == null ? "" : message.lines().findFirst().orElse("").replace("|", "/");
    }
}
