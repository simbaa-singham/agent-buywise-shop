-- customers and orders modules (ADR-014, ADR-010: schema per module, no cross-schema foreign keys)
CREATE SCHEMA IF NOT EXISTS customers;

CREATE TABLE customers.customers (
    customer_id text PRIMARY KEY,
    first_name  text        NOT NULL,
    last_name   text        NOT NULL,
    email       text        NOT NULL UNIQUE,
    phone       text,
    address     jsonb,
    created_at  date        NOT NULL,
    is_guest    boolean     NOT NULL DEFAULT false
);

CREATE SCHEMA IF NOT EXISTS orders;

-- Sales tax for delivery orders (pickup orders use the store's rate)
CREATE TABLE orders.sales_tax (
    state char(2)      PRIMARY KEY,
    rate  numeric(6,5) NOT NULL
);

CREATE SEQUENCE orders.order_number_seq START 200000;

CREATE TABLE orders.orders (
    order_id          text PRIMARY KEY,
    customer_id       text          NOT NULL,          -- customers module id, no FK across schemas
    placed_at         timestamp     NOT NULL,
    status            text          NOT NULL CHECK (status IN ('placed','processing','ready_for_pickup','picked_up',
                                                               'shipped','out_for_delivery','delayed','delivered','cancelled')),
    fulfilment        jsonb         NOT NULL,          -- {type: pickup|delivery, store_id | address, method}
    subtotal          numeric(10,2) NOT NULL,
    shipping_fee      numeric(10,2) NOT NULL DEFAULT 0,
    tax               numeric(10,2) NOT NULL,
    total             numeric(10,2) NOT NULL,
    payment           jsonb         NOT NULL,          -- mock payment only: {method, state}, never card data
    tracking_number   text,
    pickup_hold_until timestamp
);
CREATE INDEX orders_customer_idx ON orders.orders (customer_id, placed_at DESC);

CREATE TABLE orders.order_items (
    order_id   text          NOT NULL REFERENCES orders.orders (order_id),
    line_no    integer       NOT NULL,
    sku        text          NOT NULL,
    product_id text          NOT NULL,
    model      text          NOT NULL,
    quantity   integer       NOT NULL CHECK (quantity > 0),
    unit_price numeric(10,2) NOT NULL,
    PRIMARY KEY (order_id, line_no)
);
