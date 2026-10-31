package com.howtodoinjava.leastprivilege.auth;

import java.util.Set;

/**
 * A client registered at the authorization server: which grant it may use,
 * which scopes it may ask for, and which APIs (audiences) its tokens may target.
 */
public record OAuthClient(String clientId, String secret, String grantType,
                          Set<String> allowedScopes, Set<String> allowedAudiences) {

    public static final String CLIENT_CREDENTIALS = "client_credentials";
    public static final String TOKEN_EXCHANGE = "urn:ietf:params:oauth:grant-type:token-exchange";

    @Override
    public String toString() {
        return "OAuthClient[" + clientId + ", secret=****]";
    }
}
