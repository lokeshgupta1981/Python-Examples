package com.howtodoinjava.leastprivilege.tools;

import org.springframework.security.oauth2.client.endpoint.OAuth2ClientCredentialsGrantRequest;
import org.springframework.security.oauth2.client.endpoint.RestClientClientCredentialsTokenResponseClient;
import org.springframework.security.oauth2.client.registration.ClientRegistration;
import org.springframework.security.oauth2.core.AuthorizationGrantType;

/** Gets a token for the tool's own client with the client_credentials grant. */
public class ClientCredentialsTokens implements ReportsTokens, OrdersTokens {

    private final ClientRegistration registration;
    private final RestClientClientCredentialsTokenResponseClient client =
            new RestClientClientCredentialsTokenResponseClient();

    public ClientCredentialsTokens(String tokenUri, String clientId, String clientSecret, String... scopes) {
        this.registration = ClientRegistration.withRegistrationId(clientId)
                .clientId(clientId)
                .clientSecret(clientSecret)
                .authorizationGrantType(AuthorizationGrantType.CLIENT_CREDENTIALS)
                .scope(scopes)
                .tokenUri(tokenUri)
                .build();
    }

    @Override
    public String token() {
        return client.getTokenResponse(new OAuth2ClientCredentialsGrantRequest(registration))
                .getAccessToken().getTokenValue();
    }

    /** The shared-key setup ignores the user and uses its own all-powerful token. */
    @Override
    public String tokenFor(String userAccessToken) {
        return token();
    }
}
