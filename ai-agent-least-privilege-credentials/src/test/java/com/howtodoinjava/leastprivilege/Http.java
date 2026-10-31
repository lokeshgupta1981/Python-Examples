package com.howtodoinjava.leastprivilege;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

/** Sends a request with a bearer token, the way an attacker holding the token would. */
final class Http {

    private static final HttpClient CLIENT = HttpClient.newHttpClient();

    static HttpResponse<String> post(String url, String token) throws Exception {
        HttpRequest request = HttpRequest.newBuilder(URI.create(url))
                .header("Authorization", "Bearer " + token)
                .POST(HttpRequest.BodyPublishers.ofString("attack"))
                .build();
        return CLIENT.send(request, HttpResponse.BodyHandlers.ofString());
    }

    private Http() {
    }
}
