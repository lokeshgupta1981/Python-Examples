package com.howtodoinjava.leastprivilege.tools;

import java.time.Instant;

import org.springframework.security.oauth2.client.endpoint.RestClientTokenExchangeTokenResponseClient;
import org.springframework.security.oauth2.client.endpoint.TokenExchangeGrantRequest;
import org.springframework.security.oauth2.client.registration.ClientRegistration;
import org.springframework.security.oauth2.core.AuthorizationGrantType;
import org.springframework.security.oauth2.core.OAuth2AccessToken;
import org.springframework.security.oauth2.core.endpoint.OAuth2ParameterNames;
import org.springframework.util.LinkedMultiValueMap;

/**
 * Exchanges the signed-in user's token for a token that only the Orders API accepts,
 * with only the orders:cancel scope (RFC 8693), using Spring Security's token client.
 */
public class TokenExchangeOrdersTokens implements OrdersTokens {

    private final ClientRegistration registration;
    private final RestClientTokenExchangeTokenResponseClient client = new RestClientTokenExchangeTokenResponseClient();

    public TokenExchangeOrdersTokens(String tokenUri, String clientId, String clientSecret) {
        this.registration = ClientRegistration.withRegistrationId("orders-api")
                .clientId(clientId)
                .clientSecret(clientSecret)
                .authorizationGrantType(AuthorizationGrantType.TOKEN_EXCHANGE)
                .scope("orders:cancel")
                .tokenUri(tokenUri)
                .build();
        client.addParametersConverter(request -> {
            LinkedMultiValueMap<String, String> parameters = new LinkedMultiValueMap<>();
            parameters.set(OAuth2ParameterNames.AUDIENCE, "orders-api");
            return parameters;
        });
    }

    @Override
    public String tokenFor(String userAccessToken) {
        OAuth2AccessToken subjectToken = new OAuth2AccessToken(
                OAuth2AccessToken.TokenType.BEARER, userAccessToken, Instant.now(), Instant.now().plusSeconds(60));
        TokenExchangeGrantRequest request = new TokenExchangeGrantRequest(registration, subjectToken, null);
        return client.getTokenResponse(request).getAccessToken().getTokenValue();
    }
}
