"""Send six queries through check_sql(), then two straight to the read-only connection."""
import sqlite3

from ask import check_sql, run_query

QUERIES = [
    "SELECT name FROM products ORDER BY unit_price DESC",
    "DELETE FROM orders",
    "SELECT COUNT(*) FROM orders; DROP TABLE orders",
    "WITH gone AS (DELETE FROM orders RETURNING id) SELECT COUNT(*) FROM gone",
    "SELECT sql FROM sqlite_master",
    "PRAGMA table_info(customers)",
]

for sql in QUERIES:
    try:
        print("ALLOWED", check_sql(sql))
    except ValueError as e:
        print("BLOCKED", sql, "->", e)

# Skip the gate: the connection itself must refuse writes and stop runaway queries
try:
    run_query("DELETE FROM orders")
except sqlite3.Error as e:
    print("READ-ONLY", e)
try:
    run_query("SELECT COUNT(*) FROM order_items a, order_items b, order_items c")
except sqlite3.Error as e:
    print("TIME LIMIT", e)
