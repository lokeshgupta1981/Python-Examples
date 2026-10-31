package com.howtodoinjava.leastprivilege.auth;

import java.io.IOException;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.net.URLDecoder;
import java.nio.charset.StandardCharsets;
import java.text.ParseException;
import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.util.Arrays;
import java.util.Base64;
import java.util.Date;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

import com.nimbusds.jose.JOSEException;
import com.nimbusds.jose.JWSAlgorithm;
import com.nimbusds.jose.JWSHeader;
import com.nimbusds.jose.crypto.RSASSASigner;
import com.nimbusds.jose.jwk.RSAKey;
import com.nimbusds.jose.jwk.gen.RSAKeyGenerator;
import com.nimbusds.jose.util.JSONObjectUtils;
import com.nimbusds.jwt.JWTClaimsSet;
import com.nimbusds.jwt.SignedJWT;
import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpServer;

/**
 * A small OAuth 2.0 authorization server for the example. It supports the
 * client_credentials grant and the RFC 8693 token exchange grant, and signs
 * JWT access tokens with an RSA key. In production, this is Keycloak, Okta,
 * Spring Authorization Server or a similar product.
 */
public class AuthServer implements AutoCloseable {

    public static final String ACCESS_TOKEN_TYPE = "urn:ietf:params:oauth:token-type:access_token";

    private final RSAKey key;
    private final Map<String, OAuthClient> clients = new HashMap<>();
    private final Clock clock;
    private final HttpServer server;
    private final String issuer;

    public AuthServer(List<OAuthClient> clients, Clock clock) {
        try {
            this.key = new RSAKeyGenerator(2048).keyID("orderdesk-key-1").generate();
            this.server = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);
        } catch (JOSEException | IOException e) {
            throw new IllegalStateException(e);
        }
        clients.forEach(c -> this.clients.put(c.clientId(), c));
        this.clock = clock;
        this.issuer = "http://127.0.0.1:" + server.getAddress().getPort();
        server.createContext("/token", this::token);
        server.start();
    }

    public String issuer() {
        return issuer;
    }

    public String tokenUri() {
        return issuer + "/token";
    }

    public RSAKey publicKey() {
        return key.toPublicJWK();
    }

    /** What the login flow gives the OrderDesk web app after the user signs in. */
    public String loginToken(String userId, String clientId, String... scopes) {
        return sign(userId, List.of(clientId), String.join(" ", scopes), clientId, null, Duration.ofMinutes(15));
    }

    private void token(HttpExchange exchange) throws IOException {
        try {
            Map<String, String> form = parseForm(new String(exchange.getRequestBody().readAllBytes(),
                    StandardCharsets.UTF_8));
            OAuthClient client = authenticate(exchange.getRequestHeaders().getFirst("Authorization"));
            if (client == null) {
                send(exchange, 401, error("invalid_client", "Client authentication failed"));
                return;
            }
            String grantType = form.get("grant_type");
            if (!client.grantType().equals(grantType)) {
                send(exchange, 400, error("unauthorized_client", "Grant type not allowed for this client"));
                return;
            }
            Set<String> requested = scopes(form.get("scope"));
            if (requested.isEmpty() || !client.allowedScopes().containsAll(requested)) {
                send(exchange, 400, error("invalid_scope", "Scope not allowed for this client"));
                return;
            }
            if (OAuthClient.CLIENT_CREDENTIALS.equals(grantType)) {
                String token = sign(client.clientId(), List.copyOf(client.allowedAudiences()),
                        String.join(" ", requested), client.clientId(), null, Duration.ofMinutes(5));
                send(exchange, 200, tokenResponse(token, requested, null));
            } else {
                tokenExchange(exchange, client, form, requested);
            }
        } catch (RuntimeException e) {
            send(exchange, 400, error("invalid_request", "Malformed request"));
        }
    }

    private void tokenExchange(HttpExchange exchange, OAuthClient client, Map<String, String> form,
                               Set<String> requested) throws IOException {
        if (!ACCESS_TOKEN_TYPE.equals(form.get("subject_token_type"))) {
            send(exchange, 400, error("invalid_request", "Unsupported subject_token_type"));
            return;
        }
        String audience = form.get("audience");
        if (audience == null || !client.allowedAudiences().contains(audience)) {
            send(exchange, 400, error("invalid_target", "Audience not allowed for this client"));
            return;
        }
        JWTClaimsSet subject;
        try {
            subject = new BearerTokenValidator(publicKey(), issuer, client.clientId(), clock)
                    .validate(form.get("subject_token"));
        } catch (BearerTokenValidator.InvalidTokenException e) {
            send(exchange, 400, error("invalid_grant", "Subject token is not valid for this client"));
            return;
        }
        Set<String> userScopes = scopes((String) subject.getClaim("scope"));
        if (!userScopes.containsAll(requested)) {
            send(exchange, 400, error("invalid_scope", "The user has not granted this scope"));
            return;
        }
        Map<String, Object> actor = Map.of("sub", client.clientId());
        String token = sign(subject.getSubject(), List.of(audience), String.join(" ", requested),
                client.clientId(), actor, Duration.ofMinutes(5));
        send(exchange, 200, tokenResponse(token, requested, ACCESS_TOKEN_TYPE));
    }

    private String sign(String subject, List<String> audience, String scope, String clientId,
                        Map<String, Object> actor, Duration ttl) {
        Instant now = clock.instant();
        JWTClaimsSet.Builder claims = new JWTClaimsSet.Builder()
                .issuer(issuer)
                .subject(subject)
                .audience(audience)
                .claim("scope", scope)
                .claim("client_id", clientId)
                .issueTime(Date.from(now))
                .expirationTime(Date.from(now.plus(ttl)))
                .jwtID(UUID.randomUUID().toString());
        if (actor != null) {
            claims.claim("act", actor);
        }
        try {
            SignedJWT jwt = new SignedJWT(new JWSHeader.Builder(JWSAlgorithm.RS256).keyID(key.getKeyID()).build(),
                    claims.build());
            jwt.sign(new RSASSASigner(key));
            return jwt.serialize();
        } catch (JOSEException e) {
            throw new IllegalStateException(e);
        }
    }

    private OAuthClient authenticate(String authorization) {
        if (authorization == null || !authorization.startsWith("Basic ")) {
            return null;
        }
        String decoded = new String(Base64.getDecoder().decode(authorization.substring(6)), StandardCharsets.UTF_8);
        int colon = decoded.indexOf(':');
        String id = URLDecoder.decode(decoded.substring(0, colon), StandardCharsets.UTF_8);
        String secret = URLDecoder.decode(decoded.substring(colon + 1), StandardCharsets.UTF_8);
        OAuthClient client = clients.get(id);
        return client != null && client.secret().equals(secret) ? client : null;
    }

    private static Set<String> scopes(String scope) {
        return scope == null || scope.isBlank() ? Set.of()
                : new LinkedHashSet<>(Arrays.asList(scope.trim().split("\\s+")));
    }

    private static Map<String, String> parseForm(String body) {
        Map<String, String> form = new HashMap<>();
        for (String pair : body.split("&")) {
            int eq = pair.indexOf('=');
            if (eq > 0) {
                form.put(URLDecoder.decode(pair.substring(0, eq), StandardCharsets.UTF_8),
                        URLDecoder.decode(pair.substring(eq + 1), StandardCharsets.UTF_8));
            }
        }
        return form;
    }

    private static String tokenResponse(String token, Set<String> scopes, String issuedTokenType) {
        Map<String, Object> body = new LinkedHashMap<>();
        body.put("access_token", token);
        body.put("token_type", "Bearer");
        body.put("expires_in", 300);
        body.put("scope", String.join(" ", scopes));
        if (issuedTokenType != null) {
            body.put("issued_token_type", issuedTokenType);
        }
        return JSONObjectUtils.toJSONString(body);
    }

    private static String error(String code, String description) {
        return JSONObjectUtils.toJSONString(Map.of("error", code, "error_description", description));
    }

    private static void send(HttpExchange exchange, int status, String json) throws IOException {
        byte[] bytes = json.getBytes(StandardCharsets.UTF_8);
        exchange.getResponseHeaders().set("Content-Type", "application/json");
        exchange.getResponseHeaders().set("Cache-Control", "no-store");
        exchange.sendResponseHeaders(status, bytes.length);
        try (OutputStream out = exchange.getResponseBody()) {
            out.write(bytes);
        }
    }

    /** Reads the claims of a token without checking it. For printing and tests only. */
    public static JWTClaimsSet peek(String token) {
        try {
            return SignedJWT.parse(token).getJWTClaimsSet();
        } catch (ParseException e) {
            throw new IllegalArgumentException(e);
        }
    }

    @Override
    public void close() {
        server.stop(0);
    }
}
