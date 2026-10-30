"""Create shop.db: 300 customers, 16 products and 2,380 made-up orders for ShopSales."""
import random
import sqlite3
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).parent
DB = HERE / "shop.db"

FIRST = ["Anna", "Ben", "Clara", "David", "Eva", "Felix", "Greta", "Hugo", "Ines", "Jonas",
         "Klara", "Lukas", "Mia", "Noah", "Olivia", "Paul", "Rosa", "Simon", "Tara", "Viktor"]
LAST = ["Bauer", "Costa", "Dubois", "Eriksen", "Fischer", "Garcia", "Hansen", "Jansen",
        "Keller", "Lopez", "Moreau", "Novak", "Rossi", "Schmidt", "Weber"]
CITIES = ["Berlin", "Paris", "Madrid", "Rome", "Vienna", "Amsterdam", "Lisbon", "Prague"]
PRODUCTS = [
    ("Espresso Beans 1kg", "Coffee", 24.90), ("Filter Coffee 500g", "Coffee", 11.50),
    ("Decaf Beans 500g", "Coffee", 12.90), ("Cold Brew Pack", "Coffee", 15.00),
    ("Green Tea 100g", "Tea", 8.50), ("Earl Grey 100g", "Tea", 7.90),
    ("Chai Mix 250g", "Tea", 9.90), ("Herbal Tea Box", "Tea", 13.50),
    ("Espresso Machine", "Equipment", 449.00), ("Coffee Grinder", "Equipment", 129.00),
    ("Pour-Over Kettle", "Equipment", 59.00), ("French Press", "Equipment", 34.90),
    ("Milk Frother", "Accessories", 39.00), ("Ceramic Mug", "Accessories", 12.00),
    ("Travel Cup", "Accessories", 19.90), ("Cleaning Tablets", "Accessories", 9.50),
]
START, END = date(2025, 1, 1), date(2026, 10, 25)


def main():
    rnd = random.Random(42)
    DB.unlink(missing_ok=True)
    con = sqlite3.connect(DB)
    con.executescript("""
        CREATE TABLE customers (id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT NOT NULL,
                                city TEXT NOT NULL, signup_date TEXT NOT NULL);
        CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT NOT NULL, category TEXT NOT NULL,
                               unit_price REAL NOT NULL);
        CREATE TABLE orders (id INTEGER PRIMARY KEY, customer_id INTEGER NOT NULL REFERENCES customers(id),
                             order_date TEXT NOT NULL, status TEXT NOT NULL);
        CREATE TABLE order_items (order_id INTEGER NOT NULL REFERENCES orders(id),
                                  product_id INTEGER NOT NULL REFERENCES products(id),
                                  quantity INTEGER NOT NULL, unit_price REAL NOT NULL);
    """)
    days = (END - START).days
    for cid in range(1, 301):
        first, last = rnd.choice(FIRST), rnd.choice(LAST)
        signup = START - timedelta(days=rnd.randint(0, 400))
        con.execute("INSERT INTO customers VALUES (?, ?, ?, ?, ?)",
                    (cid, f"{first} {last}", f"{first.lower()}.{last.lower()}{cid}@example.com",
                     rnd.choice(CITIES), signup.isoformat()))
    for pid, (name, category, price) in enumerate(PRODUCTS, 1):
        con.execute("INSERT INTO products VALUES (?, ?, ?, ?)", (pid, name, category, price))
    for oid in range(1, 2381):
        day = START + timedelta(days=rnd.randint(0, days))
        status = rnd.choices(["completed", "cancelled", "refunded"], [88, 7, 5])[0]
        con.execute("INSERT INTO orders VALUES (?, ?, ?, ?)",
                    (oid, rnd.randint(1, 300), day.isoformat(), status))
        for pid in rnd.sample(range(1, 17), rnd.choices([1, 2, 3], [60, 30, 10])[0]):
            price = PRODUCTS[pid - 1][2]
            paid = round(price * rnd.choice([1.0, 1.0, 1.0, 0.9, 0.8]), 2)  # some discounts
            qty = 1 if price > 100 else rnd.randint(1, 4)
            con.execute("INSERT INTO order_items VALUES (?, ?, ?, ?)", (oid, pid, qty, paid))
    con.commit()
    counts = [con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
              for t in ("customers", "products", "orders", "order_items")]
    con.close()
    print(f"created {DB.name}: {counts[0]} customers, {counts[1]} products, "
          f"{counts[2]} orders, {counts[3]} order items")


if __name__ == "__main__":
    main()
