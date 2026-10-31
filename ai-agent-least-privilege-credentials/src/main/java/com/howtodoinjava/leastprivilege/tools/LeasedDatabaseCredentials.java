package com.howtodoinjava.leastprivilege.tools;

import java.time.Clock;
import java.time.Duration;

import com.howtodoinjava.leastprivilege.db.DatabaseCredentialBroker;
import com.howtodoinjava.leastprivilege.db.DbCredential;

/**
 * Keeps one short-lived database user and asks the broker for a new one shortly
 * before it expires, so the tool never runs with a login that is about to be dropped.
 */
public class LeasedDatabaseCredentials implements DatabaseCredentials {

    private final DatabaseCredentialBroker broker;
    private final String role;
    private final Duration renewBefore;
    private final Clock clock;
    private DbCredential lease;

    public LeasedDatabaseCredentials(DatabaseCredentialBroker broker, String role, Duration renewBefore, Clock clock) {
        this.broker = broker;
        this.role = role;
        this.renewBefore = renewBefore;
        this.clock = clock;
    }

    @Override
    public synchronized DbCredential current() {
        if (lease == null || !clock.instant().plus(renewBefore).isBefore(lease.expiresAt())) {
            lease = broker.issue(role);
        }
        return lease;
    }
}
