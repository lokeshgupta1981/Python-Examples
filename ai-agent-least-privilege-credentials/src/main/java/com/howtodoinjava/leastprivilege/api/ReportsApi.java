package com.howtodoinjava.leastprivilege.api;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.Map;
import java.util.concurrent.CopyOnWriteArrayList;

import com.howtodoinjava.leastprivilege.auth.BearerTokenValidator;
import com.nimbusds.jwt.JWTClaimsSet;
import com.sun.net.httpserver.HttpExchange;

/** POST /reports. Needs a token for audience "reports-api" with scope "reports:send". */
public class ReportsApi extends ProtectedApi {

    public static final String AUDIENCE = "reports-api";

    private final List<String> reports = new CopyOnWriteArrayList<>();

    public ReportsApi(BearerTokenValidator validator) {
        super(validator, "/reports");
    }

    @Override
    void handle(HttpExchange exchange, JWTClaimsSet claims) throws IOException {
        if (!hasScope(claims, "reports:send")) {
            insufficientScope(exchange, "reports:send");
            return;
        }
        reports.add(new String(exchange.getRequestBody().readAllBytes(), StandardCharsets.UTF_8));
        send(exchange, 202, Map.of("status", "queued"));
    }

    public List<String> reports() {
        return List.copyOf(reports);
    }
}
