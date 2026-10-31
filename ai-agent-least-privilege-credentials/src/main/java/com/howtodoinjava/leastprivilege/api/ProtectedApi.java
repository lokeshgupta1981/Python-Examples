package com.howtodoinjava.leastprivilege.api;

import java.io.IOException;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.Map;

import com.howtodoinjava.leastprivilege.auth.BearerTokenValidator;
import com.nimbusds.jose.util.JSONObjectUtils;
import com.nimbusds.jwt.JWTClaimsSet;
import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpServer;

/** An HTTP API that accepts only access tokens issued for it, with the scope it needs. */
abstract class ProtectedApi implements AutoCloseable {

    private final HttpServer server;
    private final BearerTokenValidator validator;

    ProtectedApi(BearerTokenValidator validator, String path) {
        this.validator = validator;
        try {
            this.server = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);
        } catch (IOException e) {
            throw new IllegalStateException(e);
        }
        server.createContext(path, this::dispatch);
        server.start();
    }

    public String baseUrl() {
        return "http://127.0.0.1:" + server.getAddress().getPort();
    }

    private void dispatch(HttpExchange exchange) throws IOException {
        String header = exchange.getRequestHeaders().getFirst("Authorization");
        JWTClaimsSet claims;
        try {
            claims = validator.validate(header != null && header.startsWith("Bearer ") ? header.substring(7) : null);
        } catch (BearerTokenValidator.InvalidTokenException e) {
            exchange.getResponseHeaders().set("WWW-Authenticate",
                    "Bearer error=\"invalid_token\", error_description=\"" + e.getMessage() + "\"");
            send(exchange, 401, Map.of("error", "invalid_token", "reason", e.getMessage()));
            return;
        }
        handle(exchange, claims);
    }

    abstract void handle(HttpExchange exchange, JWTClaimsSet claims) throws IOException;

    static boolean hasScope(JWTClaimsSet claims, String scope) {
        Object value = claims.getClaim("scope");
        return value != null && Arrays.asList(value.toString().split(" ")).contains(scope);
    }

    static void insufficientScope(HttpExchange exchange, String scope) throws IOException {
        exchange.getResponseHeaders().set("WWW-Authenticate",
                "Bearer error=\"insufficient_scope\", scope=\"" + scope + "\"");
        send(exchange, 403, Map.of("error", "insufficient_scope", "scope", scope));
    }

    static void send(HttpExchange exchange, int status, Map<String, Object> body) throws IOException {
        byte[] bytes = JSONObjectUtils.toJSONString(body).getBytes(StandardCharsets.UTF_8);
        exchange.getResponseHeaders().set("Content-Type", "application/json");
        exchange.sendResponseHeaders(status, bytes.length);
        try (OutputStream out = exchange.getResponseBody()) {
            out.write(bytes);
        }
    }

    @Override
    public void close() {
        server.stop(0);
    }
}
