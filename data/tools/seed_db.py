"""Seed job (phase 0, seed Option B): load data/seed into the `services` database.

Runs after Flyway has applied the schema (`make migrate`). Idempotent: each run replaces the
seeded tables in one transaction. Phase 0 loads catalog + inventory only; customers, orders
and tickets are loaded once their modules exist (customers need field encryption, ADR-036).
"""
import json
import os
from pathlib import Path

import psycopg
from psycopg.types.json import Jsonb

SEED = Path(__file__).resolve().parents[1] / "seed"
DSN = os.environ.get("SERVICES_DATABASE_URL", "postgresql://services:services-local@localhost:5432/services")


def load(name):
    return json.loads((SEED / name).read_text())


def main():
    products = []
    for f in ["phones", "tablets", "laptops", "watches", "audio", "accessories"]:
        products += load(f"catalog/{f}.json")
    compat = load("catalog/compatibility.json")
    stores, stock = load("stores.json"), load("stock.json")

    with psycopg.connect(DSN) as conn, conn.cursor() as cur:
        cur.execute("TRUNCATE catalog.compatibility, catalog.price_history, catalog.variants, catalog.products, "
                    "inventory.stock, inventory.stores")
        for p in products:
            cur.execute(
                "INSERT INTO catalog.products (product_id, brand_id, category, family, model, release_date, "
                "availability, specs, compatibility_tags, fits_tags, compatibility_note, specs_verified, image) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,NULL)",
                (p["product_id"], p["brand_id"], p["category"], p["family"], p["model"], p["release_date"],
                 p["availability"], Jsonb(p["specs"]), p.get("compatibility_tags", []), p.get("fits_tags", []),
                 p.get("compatibility_note"), p["specs_verified"]))
            for v in p["variants"]:
                cur.execute(
                    "INSERT INTO catalog.variants (sku, product_id, storage_gb, size, color, list_price, price_verified) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s)",
                    (v["sku"], p["product_id"], v.get("storage_gb"), v.get("size"), v["color"], v["list_price"],
                     v["price_verified"]))
                for h in v.get("price_history", []):
                    cur.execute(
                        "INSERT INTO catalog.price_history (sku, list_price, effective_from, effective_to) "
                        "VALUES (%s,%s,%s,%s)",
                        (v["sku"], h["list_price"], None if h["effective_from"] == "launch" else h["effective_from"],
                         h["effective_to"]))
        cur.executemany("INSERT INTO catalog.compatibility VALUES (%s,%s,%s,%s)",
                        [(c["accessory_id"], c["device_id"], c["compatible"], c["note"]) for c in compat])
        cur.executemany(
            "INSERT INTO inventory.stores VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            [(s["store_id"], s["name"], s["address"], s["city"], s["state"], s["zip"], s["timezone"],
              s["sales_tax_rate"], Jsonb(s["hours"]), s["same_day_radius_miles"]) for s in stores])
        cur.executemany("INSERT INTO inventory.stock VALUES (%s,%s,%s)",
                        [(r["sku"], r["store_id"], r["quantity"]) for r in stock])
        for t in ["catalog.products", "catalog.variants", "catalog.price_history", "catalog.compatibility",
                  "inventory.stores", "inventory.stock"]:
            cur.execute(f"SELECT count(*) FROM {t}")
            print(f"{t}: {cur.fetchone()[0]}")


if __name__ == "__main__":
    main()
