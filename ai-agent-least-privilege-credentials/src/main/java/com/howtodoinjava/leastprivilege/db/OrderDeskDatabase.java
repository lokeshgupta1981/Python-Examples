package com.howtodoinjava.leastprivilege.db;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.sql.Statement;

/**
 * The OrderDesk database: an in-memory H2 database with real users and grants.
 * The owner account creates the tables; tools never get it in the scoped setup.
 */
public class OrderDeskDatabase {

    private final String url;
    private final String ownerUser = "ORDERDESK_OWNER";
    private final String ownerPassword;
    private final Connection keepAlive;

    public OrderDeskDatabase(String name, String ownerPassword) {
        this.url = "jdbc:h2:mem:" + name;
        this.ownerPassword = ownerPassword;
        try {
            // An in-memory H2 database lives as long as one connection to it is open.
            this.keepAlive = DriverManager.getConnection(url, ownerUser, ownerPassword);
        } catch (SQLException e) {
            throw new IllegalStateException("Cannot create the OrderDesk database", e);
        }
        try (Statement s = keepAlive.createStatement()) {
            s.execute("""
                    CREATE TABLE customers (id VARCHAR(10) PRIMARY KEY, name VARCHAR(50),
                                            email VARCHAR(80), card_last4 CHAR(4))""");
            s.execute("""
                    CREATE TABLE orders (id VARCHAR(10) PRIMARY KEY, customer_id VARCHAR(10),
                                         item VARCHAR(80), total DECIMAL(10,2), status VARCHAR(20))""");
            s.execute("""
                    INSERT INTO customers VALUES
                      ('C-42', 'Asha Rao', 'asha@example.com', '4242'),
                      ('C-77', 'Ben Ortiz', 'ben@example.com', '7777')""");
            s.execute("""
                    INSERT INTO orders VALUES
                      ('A-1001', 'C-42', 'Coffee grinder', 89.00, 'SHIPPED'),
                      ('A-1002', 'C-42', 'Espresso machine', 450.00, 'PROCESSING'),
                      ('B-2001', 'C-77', 'Milk frother', 60.00, 'PROCESSING')""");
        } catch (SQLException e) {
            throw new IllegalStateException("Cannot create the OrderDesk database", e);
        }
    }

    public String url() {
        return url;
    }

    /** The owner connection. Only the broker and the Orders API use it. */
    public Connection ownerConnection() throws SQLException {
        return DriverManager.getConnection(url, ownerUser, ownerPassword);
    }

    public Connection connect(String user, String password) throws SQLException {
        return DriverManager.getConnection(url, user, password);
    }

    public String ownerUser() {
        return ownerUser;
    }

    public String ownerPassword() {
        return ownerPassword;
    }
}
