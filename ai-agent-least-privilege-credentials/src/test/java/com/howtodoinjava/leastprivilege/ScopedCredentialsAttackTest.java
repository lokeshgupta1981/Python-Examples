package com.howtodoinjava.leastprivilege;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import java.net.http.HttpResponse;
import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.time.Duration;
import java.time.Instant;
import java.util.Map;

import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.ai.chat.model.ToolContext;
import org.springframework.security.oauth2.core.OAuth2AuthorizationException;

import com.howtodoinjava.leastprivilege.auth.AuthServer;
import com.howtodoinjava.leastprivilege.db.DbCredential;
import com.howtodoinjava.leastprivilege.tools.ClientCredentialsTokens;
import com.nimbusds.jwt.JWTClaimsSet;

/**
 * Each attack takes the credential a tool really holds and uses it the way an attacker
 * who controls that tool would. With scoped credentials, every attack fails.
 */
class ScopedCredentialsAttackTest {

    private MutableClock clock;
    private OrderDesk desk;
    private String ashaToken;

    @BeforeEach
    void setUp() {
        clock = new MutableClock(Instant.now());
        desk = OrderDesk.scoped(clock);
        ashaToken = desk.signIn("C-42");
    }

    @AfterEach
    void tearDown() {
        desk.close();
    }

    private ToolContext asha() {
        return new ToolContext(Map.of("customerId", "C-42", "userAccessToken", ashaToken));
    }

    @Test
    void findOrdersReturnsOnlyTheSignedInCustomersOrders() {
        assertThat(desk.tools.findOrders(asha())).isEqualTo("""
                A-1001: Coffee grinder, 89.00 USD, SHIPPED
                A-1002: Espresso machine, 450.00 USD, PROCESSING""");
    }

    @Test
    void readOnlyLoginCannotDropOrChangeOrders() throws SQLException {
        DbCredential login = desk.findOrdersLogin.current();
        try (Connection c = desk.database.connect(login.username(), login.password());
             Statement s = c.createStatement()) {
            assertThatThrownBy(() -> s.execute("DROP TABLE orders"))
                    .hasMessageContaining("Not enough rights");
            assertThatThrownBy(() -> s.executeUpdate("UPDATE orders SET status = 'CANCELLED'"))
                    .hasMessageContaining("Not enough rights");
        }
    }

    @Test
    void readOnlyLoginCannotReadCustomers() throws SQLException {
        DbCredential login = desk.findOrdersLogin.current();
        try (Connection c = desk.database.connect(login.username(), login.password());
             Statement s = c.createStatement()) {
            assertThatThrownBy(() -> s.executeQuery("SELECT email, card_last4 FROM customers"))
                    .hasMessageContaining("Not enough rights");
        }
    }

    @Test
    void leakedDatabaseLoginStopsWorkingWhenTheLeaseExpires() {
        DbCredential login = desk.findOrdersLogin.current();
        clock.advance(Duration.ofMinutes(5));
        assertThat(desk.broker.revokeExpired()).isEqualTo(1);

        assertThatThrownBy(() -> desk.database.connect(login.username(), login.password()))
                .hasMessageContaining("Wrong user name or password");
    }

    @Test
    void findOrdersGetsANewLoginBeforeTheOldOneExpires() {
        DbCredential first = desk.findOrdersLogin.current();
        clock.advance(Duration.ofSeconds(4 * 60 + 31));
        DbCredential second = desk.findOrdersLogin.current();

        assertThat(second.username()).isNotEqualTo(first.username());
        assertThat(desk.tools.findOrders(asha())).startsWith("A-1001");
    }

    @Test
    void exchangedTokenIsForOneUserOneApiAndOneScope() throws Exception {
        String token = desk.cancelOrderTokens.tokenFor(ashaToken);
        JWTClaimsSet claims = AuthServer.peek(token);

        assertThat(claims.getSubject()).isEqualTo("C-42");
        assertThat(claims.getAudience()).containsExactly("orders-api");
        assertThat(claims.getStringClaim("scope")).isEqualTo("orders:cancel");
        assertThat(claims.getJSONObjectClaim("act")).containsEntry("sub", "orderdesk-agent");
        assertThat(Duration.between(claims.getIssueTime().toInstant(), claims.getExpirationTime().toInstant()))
                .isEqualTo(Duration.ofMinutes(5));
    }

    @Test
    void cancelOrderCannotCancelAnotherCustomersOrder() throws Exception {
        assertThat(desk.tools.cancelOrder("B-2001", asha()))
                .isEqualTo("Not allowed: order B-2001 can't be cancelled for this customer.");

        String token = desk.cancelOrderTokens.tokenFor(ashaToken);
        HttpResponse<String> response = Http.post(desk.ordersApi.baseUrl() + "/orders/B-2001/cancel", token);
        assertThat(response.statusCode()).isEqualTo(403);
        assertThat(desk.ordersApi.cancellations()).isEmpty();
    }

    @Test
    void cancelOrderWorksForTheCustomersOwnOrder() {
        assertThat(desk.tools.cancelOrder("A-1002", asha())).isEqualTo("Order A-1002 is cancelled.");
        assertThat(desk.ordersApi.cancellations()).singleElement()
                .hasToString("Cancellation[orderId=A-1002, subject=C-42, actor=orderdesk-agent]");
    }

    @Test
    void ordersTokenIsRejectedByTheReportsApi() throws Exception {
        String token = desk.cancelOrderTokens.tokenFor(ashaToken);
        HttpResponse<String> response = Http.post(desk.reportsApi.baseUrl() + "/reports", token);

        assertThat(response.statusCode()).isEqualTo(401);
        assertThat(response.headers().firstValue("WWW-Authenticate")).hasValueSatisfying(
                h -> assertThat(h).contains("wrong audience"));
    }

    @Test
    void reportsTokenCannotCancelOrders() throws Exception {
        String token = desk.sendReportTokens.token();
        HttpResponse<String> response = Http.post(desk.ordersApi.baseUrl() + "/orders/A-1001/cancel", token);

        assertThat(response.statusCode()).isEqualTo(401);
        assertThat(response.body()).contains("wrong audience");
    }

    @Test
    void reportsClientCannotAskForTheCancelScope() {
        ClientCredentialsTokens greedy = new ClientCredentialsTokens(desk.authServer.tokenUri(),
                "orderdesk-reports", desk.secrets.get("reports"), "reports:send", "orders:cancel");

        assertThatThrownBy(greedy::token)
                .isInstanceOf(OAuth2AuthorizationException.class)
                .hasMessageContaining("invalid_scope");
    }

    @Test
    void agentCannotGetACancelTokenWithoutAUser() {
        ClientCredentialsTokens agentAlone = new ClientCredentialsTokens(desk.authServer.tokenUri(),
                "orderdesk-agent", desk.secrets.get("agent"), "orders:cancel");

        assertThatThrownBy(agentAlone::token)
                .isInstanceOf(OAuth2AuthorizationException.class)
                .hasMessageContaining("unauthorized_client");
    }

    @Test
    void stolenOrdersTokenStopsWorkingAfterFiveMinutes() throws Exception {
        String token = desk.cancelOrderTokens.tokenFor(ashaToken);
        clock.advance(Duration.ofMinutes(5));

        HttpResponse<String> response = Http.post(desk.ordersApi.baseUrl() + "/orders/A-1002/cancel", token);
        assertThat(response.statusCode()).isEqualTo(401);
        assertThat(response.body()).contains("expired");
    }

    @Test
    void nothingCanBeExchangedOnceTheUserSessionHasExpired() {
        clock.advance(Duration.ofMinutes(15));

        assertThatThrownBy(() -> desk.cancelOrderTokens.tokenFor(ashaToken))
                .isInstanceOf(OAuth2AuthorizationException.class)
                .hasMessageContaining("invalid_grant");
    }

    @Test
    void databaseOwnerIsUntouched() throws SQLException {
        try (Connection c = desk.database.ownerConnection(); Statement s = c.createStatement();
             ResultSet rs = s.executeQuery("SELECT COUNT(*) FROM orders WHERE status <> 'CANCELLED'")) {
            rs.next();
            assertThat(rs.getInt(1)).isEqualTo(3);
        }
    }
}
