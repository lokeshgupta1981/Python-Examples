package com.howtodoinjava.leastprivilege;

import java.time.Clock;
import java.util.Map;
import java.util.TreeMap;

import com.howtodoinjava.leastprivilege.auth.AuthServer;
import com.howtodoinjava.leastprivilege.db.DbCredential;

/** Prints the credentials each tool receives in the scoped setup, with secrets masked. */
public class ShowTokens {

    public static void main(String[] args) throws Exception {
        try (OrderDesk desk = OrderDesk.scoped(Clock.systemUTC())) {
            String userToken = desk.signIn("C-42");
            print("Signed-in user's token", userToken);
            print("cancelOrder token (exchanged)", desk.cancelOrderTokens.tokenFor(userToken));
            print("sendReport token (client credentials)", desk.sendReportTokens.token());
            DbCredential login = desk.findOrdersLogin.current();
            System.out.println("findOrders login: " + login);
        }
    }

    private static void print(String title, String token) throws Exception {
        Map<String, Object> claims = new TreeMap<>(AuthServer.peek(token).toJSONObject());
        claims.keySet().removeAll(java.util.List.of("iss", "iat", "jti"));
        long ttl = (Long) claims.remove("exp") - AuthServer.peek(token).getIssueTime().getTime() / 1000;
        System.out.println(title + ": " + claims + ", lifetime " + ttl + " s");
    }
}
