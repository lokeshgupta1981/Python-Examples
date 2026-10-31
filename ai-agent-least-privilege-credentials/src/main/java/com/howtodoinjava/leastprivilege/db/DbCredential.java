package com.howtodoinjava.leastprivilege.db;

import java.time.Instant;

/** A database user name and password, valid until expiresAt. */
public record DbCredential(String username, String password, Instant expiresAt) {

    @Override
    public String toString() {
        return "DbCredential[username=" + username + ", password=****, expiresAt=" + expiresAt + "]";
    }
}
