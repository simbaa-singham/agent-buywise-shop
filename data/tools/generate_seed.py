"""Synthetic seed data (ADR-033): stores, stock, customers, staff, orders, tickets.

Fake people only: emails under example.com, phone numbers in the 555-0100..0199
fictional range. Fixed random seed -> identical output on every run.
Rules follow data/knowledge/_outline/policy_outline.md (shipping v1 in force today).

Output: data/seed/*.json
"""
import json
import random
from datetime import date, datetime, timedelta, time
from pathlib import Path

from faker import Faker

SEED = 20261028
TODAY = date(2026, 10, 28)
ROOT = Path(__file__).resolve().parents[1]
CAT = ROOT / "seed" / "catalog"
OUT = ROOT / "seed"

rnd = random.Random(SEED)
fake = Faker("en_US")
Faker.seed(SEED)

STORES = [
    ("st-aus", "BuyWise Austin", "Austin", "TX", "78701", "America/Chicago", 0.0825),
    ("st-sjc", "BuyWise San Jose", "San Jose", "CA", "95113", "America/Los_Angeles", 0.09375),
    ("st-bkn", "BuyWise Brooklyn", "Brooklyn", "NY", "11201", "America/New_York", 0.08875),
    ("st-chi", "BuyWise Chicago", "Chicago", "IL", "60601", "America/Chicago", 0.1025),
    ("st-sea", "BuyWise Seattle", "Seattle", "WA", "98101", "America/Los_Angeles", 0.1035),
    ("st-mia", "BuyWise Miami", "Miami", "FL", "33130", "America/New_York", 0.07),
    ("st-den", "BuyWise Denver", "Denver", "CO", "80202", "America/Denver", 0.0881),
    ("st-atl", "BuyWise Atlanta", "Atlanta", "GA", "30303", "America/New_York", 0.089),
    ("st-bos", "BuyWise Boston", "Boston", "MA", "02108", "America/New_York", 0.0625),
    ("st-phx", "BuyWise Phoenix", "Phoenix", "AZ", "85004", "America/Phoenix", 0.086),
]
HOURS = {"mon_sat": "10:00-21:00", "sun": "11:00-18:00"}

# Approximate combined sales tax used for deliveries, by state (sample data).
STATE_TAX = {
    "AL": .0924, "AK": .0182, "AZ": .0837, "AR": .0945, "CA": .0882, "CO": .0781, "CT": .0635, "DE": 0.0,
    "DC": .06, "FL": .0702, "GA": .0738, "HI": .0450, "ID": .0603, "IL": .0886, "IN": .07, "IA": .0694,
    "KS": .0865, "KY": .06, "LA": .0956, "ME": .055, "MD": .06, "MA": .0625, "MI": .06, "MN": .0804,
    "MS": .0706, "MO": .0841, "MT": 0.0, "NE": .0697, "NV": .0824, "NH": 0.0, "NJ": .066, "NM": .0762,
    "NY": .0853, "NC": .07, "ND": .0704, "OH": .0723, "OK": .0899, "OR": 0.0, "PA": .0634, "RI": .07,
    "SC": .0749, "SD": .0611, "TN": .0955, "TX": .082, "UT": .0719, "VT": .0636, "VA": .0577,
    "WA": .0938, "WV": .0657, "WI": .0570, "WY": .0544,
}
STORE_STATES = {s[3] for s in STORES}


def load_catalog():
    products = []
    for f in ["phones", "tablets", "laptops", "watches", "audio", "accessories"]:
        products += json.loads((CAT / f"{f}.json").read_text())
    return products


def price_on(variant, d):
    for h in variant.get("price_history", []):
        start = date.min if h["effective_from"] == "launch" else date.fromisoformat(h["effective_from"])
        end = date.max if h["effective_to"] is None else date.fromisoformat(h["effective_to"])
        if start <= d < end:
            return h["list_price"]
    return variant["list_price"]


def gen_stores():
    return [{"store_id": i, "name": n, "city": c, "state": s, "zip": z, "timezone": tz,
             "address": f"{rnd.randint(100, 999)} {fake.street_name()}", "sales_tax_rate": t,
             "hours": HOURS, "same_day_radius_miles": 20} for i, n, c, s, z, tz, t in STORES]


def gen_stock(products, stores):
    rows = []
    for p in products:
        for v in p["variants"]:
            for s in stores:
                if p["availability"].startswith("preorder"):
                    qty = 0
                else:
                    r = rnd.random()
                    qty = 0 if r < 0.10 else rnd.randint(1, 2) if r < 0.22 else rnd.randint(3, 40)
                rows.append({"sku": v["sku"], "store_id": s["store_id"], "quantity": qty})
    return rows


_used_phones = {"(512) 555-0100"}


def phone(i):
    while True:
        p = f"({rnd.randint(201, 989)}) 555-01{i % 100:02d}"
        if p not in _used_phones:
            _used_phones.add(p)
            return p


def gen_customers(n=500):
    custs = []
    states = list(STATE_TAX)
    for i in range(n):
        first, last = fake.first_name(), fake.last_name()
        st = rnd.choice(sorted(STORE_STATES)) if rnd.random() < 0.6 else rnd.choice(states)
        if i in (7, 8):
            st = ["AK", "HI"][i - 7]  # guaranteed Alaska / Hawaii customers
        custs.append({"customer_id": f"cu-{i + 1:04d}", "first_name": first, "last_name": last,
                      "email": f"{first.lower()}.{last.lower()}{i}@example.com", "phone": phone(i),
                      "address": {"line1": fake.street_address(), "city": fake.city(), "state": st,
                                  "zip": fake.zipcode_in_state(st) if st not in ("DC",) else "20001"},
                      "created_at": fake.date_between(date(2024, 1, 1), date(2026, 9, 30)).isoformat(),
                      "is_guest": rnd.random() < 0.25})
    custs[0].update({"customer_id": "cu-demo", "first_name": "Demo", "last_name": "Customer",
                     "email": "customer.demo@example.com", "phone": "(512) 555-0100", "is_guest": False,
                     "address": {"line1": "100 Congress Ave", "city": "Austin", "state": "TX", "zip": "78701"}})
    return custs


def gen_staff():
    roles = ["staff", "staff", "staff", "staff_lead", "ops-admin"]
    return [{"staff_id": f"sf-{i + 1:02d}", "name": fake.name(),
             "email": f"staff{i + 1}@example.com", "role": r, "mfa_required": True}
            for i, r in enumerate(roles)]


def released(p, d):
    return p["release_date"] is None or date.fromisoformat(p["release_date"]) <= d


def ship_fee(method, subtotal, state):
    if method == "standard":
        return 0.0 if subtotal > 50 else 5.99  # shipping policy v1 (in force until 2026-11-15)
    if method == "express":
        return 14.99
    return 9.99  # same_day


def status_for(age_days, fulfilment, method):
    if rnd.random() < 0.03:
        return "cancelled"
    if fulfilment == "pickup":
        if age_days == 0:
            return rnd.choice(["placed", "processing", "ready_for_pickup"])
        if age_days <= 7:
            return rnd.choice(["ready_for_pickup", "picked_up", "picked_up"])
        return "picked_up"
    if rnd.random() < 0.03 and age_days < 14:
        return "delayed"
    span = {"same_day": 0, "express": 2, "standard": 5}[method]
    if age_days == 0:
        return rnd.choice(["placed", "processing"])
    if age_days <= span:
        return rnd.choice(["shipped", "out_for_delivery"])
    return "delivered"


def gen_orders(products, customers, stores, n=2000):
    orders = []
    devices = [p for p in products if p["category"] != "accessory"]
    accessories = [p for p in products if p["category"] == "accessory"]
    by_state = {s["state"]: s for s in stores}
    start = date(2026, 1, 2)
    for i in range(n):
        cust = customers[0] if i < 12 else rnd.choice(customers)
        d = TODAY - timedelta(days=i % 12) if i < 12 else start + timedelta(days=rnd.randint(0, (TODAY - start).days))
        avail = [p for p in devices if released(p, d) and not p["availability"].startswith("preorder")]
        items, phone_counts = [], {}
        for _ in range(rnd.choices([1, 2, 3], [0.6, 0.3, 0.1])[0]):
            p = rnd.choice(avail if rnd.random() < 0.7 else accessories)
            v = rnd.choice(p["variants"])
            qty = 1 if rnd.random() < 0.85 else 2
            if p["category"] == "phone":  # policy: max 2 of the same phone model per order
                qty = min(qty, 2 - phone_counts.get(p["product_id"], 0))
                if qty <= 0:
                    continue
                phone_counts[p["product_id"]] = phone_counts.get(p["product_id"], 0) + qty
            items.append({"sku": v["sku"], "product_id": p["product_id"], "model": p["model"],
                          "quantity": qty, "unit_price": price_on(v, d)})
        if not items:
            continue
        subtotal = round(sum(it["unit_price"] * it["quantity"] for it in items), 2)
        state = cust["address"]["state"]
        pickup = state in by_state and rnd.random() < 0.35
        if pickup:
            store = by_state[state]
            fulfil = {"type": "pickup", "store_id": store["store_id"]}
            tax_rate, fee, method = store["sales_tax_rate"], 0.0, None
        else:
            method = rnd.choices(["standard", "express", "same_day"], [0.7, 0.25, 0.05])[0]
            if method == "same_day" and state not in by_state:
                method = "standard"
            if state in ("AK", "HI") and method == "same_day":
                method = "standard"
            fulfil = {"type": "delivery", "method": method, "address": cust["address"],
                      "signature_required": subtotal > 500}
            tax_rate, fee = STATE_TAX[state], ship_fee(method, subtotal, state)
        age = (TODAY - d).days
        status = status_for(age, fulfil["type"], method)
        if status == "cancelled" and age <= 1 and rnd.random() < 0.5:
            status = "placed"
        tax = round(subtotal * tax_rate, 2)
        o = {"order_id": f"BW-{100000 + i}", "customer_id": cust["customer_id"],
             "placed_at": datetime.combine(d, time(rnd.randint(8, 21), rnd.randint(0, 59))).isoformat(),
             "status": status, "items": items, "fulfilment": fulfil, "subtotal": subtotal,
             "shipping_fee": fee, "tax": tax, "total": round(subtotal + fee + tax, 2),
             "payment": {"method": rnd.choice(["card", "digital_wallet"]), "state": None}}
        finalize(o, d)
        orders.append(o)
    # Guarantee the demo customer has one order in each interesting status.
    demo_statuses = ["placed", "processing", "shipped", "out_for_delivery", "delivered", "delayed",
                     "ready_for_pickup", "picked_up", "cancelled"]
    demo = [o for o in orders if o["customer_id"] == "cu-demo"]
    aus = by_state["TX"]
    for o, s in zip(demo, demo_statuses):
        o["status"] = s
        if s in ("ready_for_pickup", "picked_up"):
            o["fulfilment"] = {"type": "pickup", "store_id": aus["store_id"]}
            o["shipping_fee"] = 0.0
        elif o["fulfilment"]["type"] == "pickup":
            o["fulfilment"] = {"type": "delivery", "method": "standard", "address": customers[0]["address"],
                               "signature_required": o["subtotal"] > 500}
            o["shipping_fee"] = ship_fee("standard", o["subtotal"], "TX")
        o["total"] = round(o["subtotal"] + o["shipping_fee"] + o["tax"], 2)
        finalize(o, date.fromisoformat(o["placed_at"][:10]))
    return orders


def finalize(o, d):
    """Keep payment, tracking and pickup-hold fields consistent with status."""
    s = o["status"]
    o["payment"]["state"] = ("authorized" if s in ("placed", "processing", "ready_for_pickup")
                             else "released" if s == "cancelled" else "captured")
    o.pop("tracking_number", None)
    o.pop("pickup_hold_until", None)
    if o["fulfilment"]["type"] == "delivery" and s in ("shipped", "out_for_delivery", "delivered", "delayed"):
        o["tracking_number"] = f"1Z{rnd.randint(10 ** 15, 10 ** 16 - 1)}"
    if s == "ready_for_pickup":
        o["pickup_hold_until"] = (d + timedelta(days=7)).isoformat()


def gen_tickets(orders, customers, staff, n=100):
    cats = [("return_request", "Customer asks to return an item (out of scope for the assistant)."),
            ("warranty_claim", "Customer reports a defect and wants to start a warranty claim."),
            ("delivery_issue", "Package delayed or marked delivered but not received."),
            ("pickup_change", "Customer wants to change pickup store or alternate pickup person."),
            ("payment_link", "Payment link expired or failed."),
            ("order_change", "Customer wants to change an order already in processing.")]
    tickets = []
    agents = [s for s in staff if s["role"] in ("staff", "staff_lead")]
    for i in range(n):
        o = rnd.choice(orders)
        cat, summary = rnd.choice(cats)
        status = rnd.choices(["open", "assigned", "resolved"], [0.2, 0.2, 0.6])[0]
        t = {"ticket_id": f"TK-{5000 + i}", "customer_id": o["customer_id"], "order_id": o["order_id"],
             "conversation_id": f"c_{rnd.getrandbits(40):010x}", "category": cat, "summary": summary,
             "status": status,
             "created_at": fake.date_time_between(datetime(2026, 1, 5), datetime(2026, 10, 27)).isoformat()}
        if status != "open":
            t["assignee"] = rnd.choice(agents)["staff_id"]
        tickets.append(t)
    return tickets


def main():
    products = load_catalog()
    stores = gen_stores()
    customers = gen_customers()
    staff = gen_staff()
    orders = gen_orders(products, customers, stores)
    out = {"stores": stores, "stock": gen_stock(products, stores), "customers": customers,
           "staff": staff, "orders": orders, "tickets": gen_tickets(orders, customers, staff),
           "sales_tax_by_state": [{"state": k, "rate": v} for k, v in STATE_TAX.items()]}
    for name, rows in out.items():
        (OUT / f"{name}.json").write_text(json.dumps(rows, indent=1) + "\n")
        print(f"{name}: {len(rows)}")


if __name__ == "__main__":
    main()
