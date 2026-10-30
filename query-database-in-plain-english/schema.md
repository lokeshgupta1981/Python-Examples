Database: SQLite. Dates are stored as text in YYYY-MM-DD format. All prices are in euros.

Table customers: one row per customer.
- id: primary key
- name: full name of the customer
- email: email address
- city: city of the customer
- signup_date: the day the customer created an account

Table products: one row per product in the catalog.
- id: primary key
- name: product name
- category: product category, one of 'Coffee', 'Tea', 'Equipment', 'Accessories'
- unit_price: the current list price per unit

Table orders: one row per order.
- id: primary key
- customer_id: joins to customers.id
- order_date: the day the order was placed
- status: one of 'completed', 'cancelled', 'refunded'

Table order_items: one row per product in an order.
- order_id: joins to orders.id
- product_id: joins to products.id
- quantity: number of units
- unit_price: the price the customer paid per unit (it can differ from products.unit_price)

Business terms:
- Revenue: SUM(order_items.quantity * order_items.unit_price) for orders with status 'completed'.
  Cancelled and refunded orders never count as revenue or as sales.
- Number of orders or sales: count only orders with status 'completed', unless the question
  asks about cancelled or refunded orders.
- Active customer: a customer with at least one completed order in the last 90 days.
- Quarters are calendar quarters (Q1 = January to March). "Last quarter" means the most recent
  quarter that has fully ended.
- "This year" means the current calendar year.
