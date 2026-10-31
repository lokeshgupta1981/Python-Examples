package com.howtodoinjava.leastprivilege.db;

import java.security.SecureRandom;
import java.sql.Connection;
import java.sql.SQLException;
import java.sql.Statement;
import java.time.Clock;
import java.time.Duration;
import java.util.HexFormat;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Issues short-lived database users the way Vault's database secrets engine does:
 * every request creates a new user from the role's creation statements, and the
 * user is dropped when its lease expires.
 */
public class DatabaseCredentialBroker {

    /** A role: the SQL that creates a user, and how long the user lives. */
    public record Role(List<String> creationStatements, Duration ttl) {
    }

    private static final SecureRandom RANDOM = new SecureRandom();

    private final OrderDeskDatabase database;
    private final Map<String, Role> roles;
    private final Clock clock;
    private final Map<String, DbCredential> leases = new ConcurrentHashMap<>();

    public DatabaseCredentialBroker(OrderDeskDatabase database, Map<String, Role> roles, Clock clock) {
        this.database = database;
        this.roles = roles;
        this.clock = clock;
    }

    public DbCredential issue(String roleName) {
        Role role = roles.get(roleName);
        if (role == null) {
            throw new IllegalArgumentException("Unknown role " + roleName);
        }
        String username = "V_" + roleName.toUpperCase().replace('-', '_') + "_" + hex(4);
        String password = hex(16);
        try (Connection c = database.ownerConnection(); Statement s = c.createStatement()) {
            for (String sql : role.creationStatements()) {
                s.execute(sql.replace("{{name}}", username).replace("{{password}}", password));
            }
        } catch (SQLException e) {
            throw new IllegalStateException("Cannot create a user for role " + roleName, e);
        }
        DbCredential credential = new DbCredential(username, password, clock.instant().plus(role.ttl()));
        leases.put(username, credential);
        return credential;
    }

    /** Drops every user whose lease has expired. Vault does this on its own; we call it on a timer. */
    public int revokeExpired() {
        int revoked = 0;
        for (DbCredential lease : List.copyOf(leases.values())) {
            if (!clock.instant().isBefore(lease.expiresAt())) {
                revoke(lease);
                revoked++;
            }
        }
        return revoked;
    }

    public void revoke(DbCredential lease) {
        try (Connection c = database.ownerConnection(); Statement s = c.createStatement()) {
            s.execute("DROP USER IF EXISTS " + lease.username());
            leases.remove(lease.username());
        } catch (SQLException e) {
            throw new IllegalStateException("Cannot drop " + lease.username(), e);
        }
    }

    private static String hex(int bytes) {
        byte[] b = new byte[bytes];
        RANDOM.nextBytes(b);
        return HexFormat.of().withUpperCase().formatHex(b);
    }
}
