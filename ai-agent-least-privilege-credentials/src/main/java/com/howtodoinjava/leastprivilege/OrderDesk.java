package com.howtodoinjava.leastprivilege;

import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

import com.howtodoinjava.leastprivilege.api.OrdersApi;
import com.howtodoinjava.leastprivilege.api.ReportsApi;
import com.howtodoinjava.leastprivilege.auth.AuthServer;
import com.howtodoinjava.leastprivilege.auth.BearerTokenValidator;
import com.howtodoinjava.leastprivilege.auth.OAuthClient;
import com.howtodoinjava.leastprivilege.db.DatabaseCredentialBroker;
import com.howtodoinjava.leastprivilege.db.DbCredential;
import com.howtodoinjava.leastprivilege.db.OrderDeskDatabase;
import com.howtodoinjava.leastprivilege.tools.ClientCredentialsTokens;
import com.howtodoinjava.leastprivilege.tools.DatabaseCredentials;
import com.howtodoinjava.leastprivilege.tools.LeasedDatabaseCredentials;
import com.howtodoinjava.leastprivilege.tools.OrderDeskTools;
import com.howtodoinjava.leastprivilege.tools.OrdersTokens;
import com.howtodoinjava.leastprivilege.tools.ReportsTokens;
import com.howtodoinjava.leastprivilege.tools.TokenExchangeOrdersTokens;

/**
 * Wires the OrderDesk example in one of two ways: every tool with the same
 * powerful credentials, or every tool with its own narrowly scoped credential.
 */
public class OrderDesk implements AutoCloseable {

    public static final String AGENT_CLIENT = "orderdesk-agent";

    public final Clock clock;
    public final OrderDeskDatabase database;
    public final AuthServer authServer;
    public final OrdersApi ordersApi;
    public final ReportsApi reportsApi;
    public final DatabaseCredentialBroker broker;
    public final DatabaseCredentials findOrdersLogin;
    public final OrdersTokens cancelOrderTokens;
    public final ReportsTokens sendReportTokens;
    public final OrderDeskTools tools;
    /** Every secret in this setup by name, so tests can check that none of them reaches the model. */
    public final Map<String, String> secrets = new LinkedHashMap<>();

    private OrderDesk(Clock clock, boolean scoped) {
        this.clock = clock;
        String ownerPassword = secret("owner");
        String agentSecret = secret("agent");
        String reportsSecret = secret("reports");
        String adminSecret = secret("admin");

        this.database = new OrderDeskDatabase("orderdesk-" + UUID.randomUUID(), ownerPassword);
        this.authServer = new AuthServer(List.of(
                new OAuthClient(AGENT_CLIENT, agentSecret, OAuthClient.TOKEN_EXCHANGE,
                        Set.of("orders:cancel"), Set.of(OrdersApi.AUDIENCE)),
                new OAuthClient("orderdesk-reports", reportsSecret, OAuthClient.CLIENT_CREDENTIALS,
                        Set.of("reports:send"), Set.of(ReportsApi.AUDIENCE)),
                new OAuthClient("orderdesk-admin", adminSecret, OAuthClient.CLIENT_CREDENTIALS,
                        Set.of("orders:cancel", "reports:send"), Set.of(OrdersApi.AUDIENCE, ReportsApi.AUDIENCE))),
                clock);
        this.ordersApi = new OrdersApi(new BearerTokenValidator(authServer.publicKey(), authServer.issuer(),
                OrdersApi.AUDIENCE, clock), database);
        this.reportsApi = new ReportsApi(new BearerTokenValidator(authServer.publicKey(), authServer.issuer(),
                ReportsApi.AUDIENCE, clock));
        this.broker = new DatabaseCredentialBroker(database, Map.of(
                "orders-reader", new DatabaseCredentialBroker.Role(List.of(
                        "CREATE USER {{name}} PASSWORD '{{password}}'",
                        "GRANT SELECT ON orders TO {{name}}"),
                        Duration.ofMinutes(5))),
                clock);

        if (scoped) {
            this.findOrdersLogin = new LeasedDatabaseCredentials(broker, "orders-reader", Duration.ofSeconds(30), clock);
            this.cancelOrderTokens = new TokenExchangeOrdersTokens(authServer.tokenUri(), AGENT_CLIENT, agentSecret);
            this.sendReportTokens = new ClientCredentialsTokens(authServer.tokenUri(), "orderdesk-reports",
                    reportsSecret, "reports:send");
        } else {
            DbCredential owner = new DbCredential(database.ownerUser(), ownerPassword, Instant.MAX);
            ClientCredentialsTokens admin = new ClientCredentialsTokens(authServer.tokenUri(), "orderdesk-admin",
                    adminSecret, "orders:cancel", "reports:send");
            this.findOrdersLogin = () -> owner;
            this.cancelOrderTokens = admin;
            this.sendReportTokens = admin;
        }
        this.tools = new OrderDeskTools(database.url(), findOrdersLogin, cancelOrderTokens, sendReportTokens,
                ordersApi.baseUrl(), reportsApi.baseUrl());
    }

    /** One powerful database account and one admin token, shared by all tools. */
    public static OrderDesk sharedKey(Clock clock) {
        return new OrderDesk(clock, false);
    }

    /** Each tool with its own narrowly scoped credential. */
    public static OrderDesk scoped(Clock clock) {
        return new OrderDesk(clock, true);
    }

    /** What the OrderDesk web app holds after the customer signs in. */
    public String signIn(String customerId) {
        return authServer.loginToken(customerId, AGENT_CLIENT, "orders:read", "orders:cancel");
    }

    private String secret(String prefix) {
        String value = prefix + "-" + UUID.randomUUID().toString().replace("-", "").substring(0, 16);
        secrets.put(prefix, value);
        return value;
    }

    @Override
    public void close() {
        authServer.close();
        ordersApi.close();
        reportsApi.close();
    }
}
