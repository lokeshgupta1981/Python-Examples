package com.howtodoinjava.leastprivilege.auth;

import java.text.ParseException;
import java.time.Clock;
import java.util.Date;

import com.nimbusds.jose.JOSEException;
import com.nimbusds.jose.crypto.RSASSAVerifier;
import com.nimbusds.jose.jwk.RSAKey;
import com.nimbusds.jwt.JWTClaimsSet;
import com.nimbusds.jwt.SignedJWT;

/**
 * Checks a JWT access token the way a resource server must: signature, issuer,
 * expiry, and that the token was issued for this API (the audience).
 */
public class BearerTokenValidator {

    public static class InvalidTokenException extends Exception {
        public InvalidTokenException(String message) {
            super(message);
        }
    }

    private final RSAKey publicKey;
    private final String issuer;
    private final String audience;
    private final Clock clock;

    public BearerTokenValidator(RSAKey publicKey, String issuer, String audience, Clock clock) {
        this.publicKey = publicKey;
        this.issuer = issuer;
        this.audience = audience;
        this.clock = clock;
    }

    public JWTClaimsSet validate(String token) throws InvalidTokenException {
        if (token == null) {
            throw new InvalidTokenException("missing token");
        }
        try {
            SignedJWT jwt = SignedJWT.parse(token);
            if (!jwt.verify(new RSASSAVerifier(publicKey))) {
                throw new InvalidTokenException("bad signature");
            }
            JWTClaimsSet claims = jwt.getJWTClaimsSet();
            if (!issuer.equals(claims.getIssuer())) {
                throw new InvalidTokenException("wrong issuer");
            }
            if (claims.getExpirationTime() == null || !claims.getExpirationTime().after(Date.from(clock.instant()))) {
                throw new InvalidTokenException("expired");
            }
            if (claims.getAudience() == null || !claims.getAudience().contains(audience)) {
                throw new InvalidTokenException("wrong audience");
            }
            return claims;
        } catch (ParseException | JOSEException e) {
            throw new InvalidTokenException("malformed token");
        }
    }
}
