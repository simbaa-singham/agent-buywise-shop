-- Load customers, orders and sales tax seed data into the services database (after Flyway V4).
-- Before running: docker cp data/seed buywise-postgres-1:/tmp/seed
-- Run as user postgres on database "services": one transaction, all or nothing.
BEGIN;

TRUNCATE orders.order_items, orders.orders, orders.sales_tax, customers.customers;

INSERT INTO customers.customers
SELECT c->>'customer_id', c->>'first_name', c->>'last_name', c->>'email', c->>'phone', c->'address',
       (c->>'created_at')::date, (c->>'is_guest')::boolean
FROM jsonb_array_elements(pg_read_file('/tmp/seed/customers.json')::jsonb) AS c;

INSERT INTO orders.sales_tax
SELECT t->>'state', (t->>'rate')::numeric
FROM jsonb_array_elements(pg_read_file('/tmp/seed/sales_tax_by_state.json')::jsonb) AS t;

CREATE TEMP VIEW seed_orders AS
SELECT o FROM jsonb_array_elements(pg_read_file('/tmp/seed/orders.json')::jsonb) AS o;

INSERT INTO orders.orders
SELECT o->>'order_id', o->>'customer_id', (o->>'placed_at')::timestamp, o->>'status', o->'fulfilment',
       (o->>'subtotal')::numeric, (o->>'shipping_fee')::numeric, (o->>'tax')::numeric, (o->>'total')::numeric,
       o->'payment', o->>'tracking_number', (o->>'pickup_hold_until')::timestamp
FROM seed_orders;

INSERT INTO orders.order_items
SELECT o->>'order_id', i.n, i.item->>'sku', i.item->>'product_id', i.item->>'model',
       (i.item->>'quantity')::int, (i.item->>'unit_price')::numeric
FROM seed_orders, jsonb_array_elements(o->'items') WITH ORDINALITY AS i(item, n);

-- Counts to check: 500 customers, 2000 orders, 51 tax rows
SELECT (SELECT count(*) FROM customers.customers) AS customers,
       (SELECT count(*) FROM orders.orders)       AS orders,
       (SELECT count(*) FROM orders.order_items)  AS items,
       (SELECT count(*) FROM orders.sales_tax)    AS tax_rates;
COMMIT;
