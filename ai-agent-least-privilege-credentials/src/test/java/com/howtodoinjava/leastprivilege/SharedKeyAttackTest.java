package com.howtodoinjava.leastprivilege;

import static org.assertj.core.api.Assertions.assertThat;

import java.net.http.HttpResponse;
import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.Statement;
import java.time.Instant;

import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import com.howtodoinjava.leastprivilege.db.DbCredential;

/** The same attacks against the shared-key setup. Every one of them works. */
class SharedKeyAttackTest {

    private OrderDesk desk;

    @BeforeEach
    void setUp() {
        desk = OrderDesk.sharedKey(new MutableClock(Instant.now()));
    }

    @AfterEach
    void tearDown() {
        desk.close();
    }

    @Test
    void findOrdersLoginCanReadCustomersAndDropOrders() throws Exception {
        DbCredential login = desk.findOrdersLogin.current();
        try (Connection c = desk.database.connect(login.username(), login.password());
             Statement s = c.createStatement()) {
            try (ResultSet rs = s.executeQuery("SELECT email, card_last4 FROM customers WHERE id = 'C-77'")) {
                rs.next();
                assertThat(rs.getString(1)).isEqualTo("ben@example.com");
            }
            s.execute("DROP TABLE orders");
        }
        assertThat(login.expiresAt()).isEqualTo(Instant.MAX);
    }

    @Test
    void cancelOrderTokenCancelsAnotherCustomersOrder() throws Exception {
        String token = desk.cancelOrderTokens.tokenFor(desk.signIn("C-42"));
        HttpResponse<String> response = Http.post(desk.ordersApi.baseUrl() + "/orders/B-2001/cancel", token);

        assertThat(response.statusCode()).isEqualTo(200);
        assertThat(desk.ordersApi.cancellations()).singleElement()
                .hasToString("Cancellation[orderId=B-2001, subject=orderdesk-admin, actor=-]");
    }

    @Test
    void reportsTokenCancelsOrders() throws Exception {
        String token = desk.sendReportTokens.token();
        HttpResponse<String> response = Http.post(desk.ordersApi.baseUrl() + "/orders/A-1001/cancel", token);

        assertThat(response.statusCode()).isEqualTo(200);
    }
}
