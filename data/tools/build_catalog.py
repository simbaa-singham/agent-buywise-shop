"""Curated product catalog (ADR-033).

Real model names, specs and US list prices, checked by web search on SPECS_VERIFIED.
The maker is never named: products carry only an opaque brand_id. No images.
`price_verified: false` marks tier prices that could not be confirmed and were derived
from the maker's usual tier steps; `null` specs were not confirmed and are left empty.

Output: data/seed/catalog/{category}.json
"""
import json
from pathlib import Path

SPECS_VERIFIED = "2026-10-28"
BRAND = "b01"
OUT = Path(__file__).resolve().parents[1] / "seed" / "catalog"


def tiers(*rows):
    """rows: (storage_gb, price, verified[, old_price, price_changed_on])"""
    out = []
    for r in rows:
        t = {"storage_gb": r[0], "list_price": r[1], "price_verified": r[2]}
        if len(r) > 3:
            t["price_history"] = [
                {"list_price": r[3], "effective_from": "launch", "effective_to": r[4]},
                {"list_price": r[1], "effective_from": r[4], "effective_to": None},
            ]
        out.append(t)
    return out


PHONES = [
    {
        "product_id": "ph-17e", "model": "iPhone 17e", "family": "iPhone", "release_date": "2026-03-11",
        "colors": ["Soft Pink", "White", "Black"],
        "tiers": tiers((256, 699, True, 599, "2026-09-09"), (512, 899, False, 799, "2026-09-09")),
        "specs": {"display": "6.1-inch Super Retina XDR OLED, 2532 x 1170, 460 ppi, 60 Hz, 1200 nits",
                  "chip": "A19 (4-core GPU)", "rear_camera": "48 MP f/1.6 26 mm, 2x optical-quality zoom",
                  "front_camera": "12 MP f/1.9", "battery_mah": 4005,
                  "wired_charging": "30 W", "wireless_charging": "MagSafe 25 W, Qi2",
                  "connector": "USB-C", "weight_g": 169, "dimensions_mm": "146.7 x 71.5 x 7.8",
                  "water_resistance": "IP68 (6 m, 30 min)"},
        "compat": ["usb-c", "magsafe", "qi2", "case:ph-17e"],
    },
    {
        "product_id": "ph-16", "model": "iPhone 16", "family": "iPhone", "release_date": "2024-09-20",
        "colors": ["Ultramarine", "Teal", "Pink", "White", "Black"],
        "tiers": tiers((128, 799, True)),
        "specs": {"display": "6.1-inch Super Retina XDR OLED, 2556 x 1179, 60 Hz",
                  "chip": "A18", "rear_camera": "48 MP wide + 12 MP ultra wide", "front_camera": "12 MP",
                  "battery_mah": 3561, "wired_charging": "up to 25 W with 30 W adapter",
                  "wireless_charging": "MagSafe", "connector": "USB-C", "weight_g": 170,
                  "dimensions_mm": "147.6 x 71.6 x 7.8", "water_resistance": "IP68 (6 m, 30 min)"},
        "compat": ["usb-c", "magsafe", "qi2", "case:ph-16"],
    },
    {
        "product_id": "ph-17", "model": "iPhone 17", "family": "iPhone", "release_date": "2025-09-19",
        "colors": ["Lavender", "Sage", "Mist Blue", "White", "Black"],
        "tiers": tiers((256, 899, True, 799, "2026-09-09"), (512, 1099, False, 999, "2026-09-09")),
        "specs": {"display": "6.3-inch Super Retina XDR OLED (LTPO), 2622 x 1206, 460 ppi, 120 Hz",
                  "chip": "A19", "rear_camera": "Dual 48 MP (main + ultra wide)",
                  "front_camera": "18 MP with Dual Capture", "battery_mah": 3692,
                  "wired_charging": "USB-C, 50% in 20 min with 40 W+ adapter",
                  "wireless_charging": "MagSafe, Qi2", "connector": "USB-C", "weight_g": 177,
                  "dimensions_mm": "149.6 x 71.5 x 7.95", "water_resistance": "IP68"},
        "compat": ["usb-c", "magsafe", "qi2", "case:ph-17"],
    },
    {
        "product_id": "ph-air", "model": "iPhone Air", "family": "iPhone", "release_date": "2025-09-19",
        "colors": ["Sky Blue", "Light Gold", "Cloud White", "Space Black"],
        "tiers": tiers((256, 1099, True, 999, "2026-09-09"), (512, 1199, False, 1099, "2026-09-09"),
                       (1024, 1399, False, 1299, "2026-09-09")),
        "specs": {"display": "6.5-inch Super Retina XDR OLED, 2736 x 1260, 460 ppi, 120 Hz, 3000 nits peak",
                  "chip": "A19 Pro", "rear_camera": "48 MP Fusion f/1.6 (single camera)",
                  "front_camera": "18 MP Center Stage", "battery_mah": 3149,
                  "wired_charging": "USB-C fast charge", "wireless_charging": "MagSafe, Qi2",
                  "connector": "USB-C (USB 2 speed)", "sim": "eSIM only", "weight_g": 165,
                  "dimensions_mm": "156.2 x 74.7 x 5.64", "water_resistance": "IP68 (6 m, 30 min)"},
        "compat": ["usb-c", "magsafe", "qi2", "case:ph-air"],
    },
    {
        "product_id": "ph-18pro", "model": "iPhone 18 Pro", "family": "iPhone", "release_date": "2026-09-18",
        "colors": ["Black", "Glacier", "Burgundy", "Silver"],
        "tiers": tiers((256, 1199, True), (512, 1399, True), (1024, 1799, True), (2048, 2399, True)),
        "specs": {"display": "6.3-inch OLED, 2622 x 1206, 120 Hz ProMotion, 3000 nits outdoor",
                  "chip": "A20 Pro", "ram_gb": 12, "rear_camera": None, "front_camera": None,
                  "battery_mah": 4288, "wired_charging": "60 W (50% in 15 min)",
                  "wireless_charging": "MagSafe, Qi2", "connector": "USB-C", "weight_g": 211,
                  "dimensions_mm": "150.0 x 71.9 x 8.75", "water_resistance": "IP68 (6 m, 30 min)"},
        "compat": ["usb-c", "magsafe", "qi2", "case:ph-18pro"],
    },
    {
        "product_id": "ph-18promax", "model": "iPhone 18 Pro Max", "family": "iPhone", "release_date": "2026-09-18",
        "colors": ["Black", "Glacier", "Burgundy", "Silver"],
        "tiers": tiers((256, 1299, True), (512, 1499, True), (1024, 1899, True), (2048, 2499, True)),
        "specs": {"display": "6.9-inch OLED, 2868 x 1320, 120 Hz ProMotion, 3000 nits outdoor",
                  "chip": "A20 Pro", "ram_gb": 12, "rear_camera": None, "front_camera": None,
                  "battery_mah": 5567, "wired_charging": "60 W", "wireless_charging": "MagSafe, Qi2",
                  "connector": "USB-C", "weight_g": 249, "dimensions_mm": "163.4 x 78.0 x 8.75",
                  "water_resistance": "IP68 (6 m, 30 min)"},
        "compat": ["usb-c", "magsafe", "qi2", "case:ph-18promax"],
    },
    {
        "product_id": "ph-duo", "model": "iPhone Duo", "family": "iPhone", "release_date": "2026-10-23",
        "colors": ["Star White", "Night Sky"],
        "tiers": tiers((256, 1999, True), (512, 2199, False), (1024, 2599, False), (2048, 3199, True)),
        "specs": {"display": "Foldable: 7.6-inch inner + 5.4-inch outer Super Retina XDR, ProMotion, 3000 nits outdoor",
                  "chip": "A20 Pro", "battery": "up to 31 hours inner-display video playback",
                  "connector": "USB-C", "wireless_charging": None, "weight_g": None, "dimensions_mm": None},
        "compat": ["usb-c", "case:ph-duo"],
    },
]

TABLETS = [
    {"product_id": "tb-ipad", "model": "iPad (A16)", "family": "iPad", "release_date": "2025-03-12",
     "colors": ["Blue", "Pink", "Yellow", "Silver"],
     "tiers": tiers((128, 349, True), (256, 449, False), (512, 649, False)),
     "specs": {"display": "11-inch Liquid Retina", "chip": "A16", "connector": "USB-C"},
     "compat": ["usb-c", "pencil-usb-c"]},
    {"product_id": "tb-mini", "model": "iPad mini (A17 Pro)", "family": "iPad", "release_date": "2024-10-23",
     "colors": ["Space Gray", "Blue", "Purple", "Starlight"],
     "tiers": tiers((128, 499, True), (256, 599, False), (512, 799, False)),
     "specs": {"display": "8.3-inch Liquid Retina", "chip": "A17 Pro", "connector": "USB-C"},
     "compat": ["usb-c", "pencil-usb-c", "pencil-pro"]},
    {"product_id": "tb-air11", "model": "iPad Air 11-inch (M4)", "family": "iPad", "release_date": "2026-03-04",
     "colors": ["Space Gray", "Blue", "Purple", "Starlight"],
     "tiers": tiers((128, 599, True), (256, 699, False), (512, 899, False), (1024, 1099, False)),
     "specs": {"display": "11-inch Liquid Retina", "chip": "M4", "connector": "USB-C"},
     "compat": ["usb-c", "pencil-usb-c", "pencil-pro"]},
    {"product_id": "tb-air13", "model": "iPad Air 13-inch (M4)", "family": "iPad", "release_date": "2026-03-04",
     "colors": ["Space Gray", "Blue", "Purple", "Starlight"],
     "tiers": tiers((128, 799, False), (256, 899, False), (512, 1099, False), (1024, 1299, False)),
     "specs": {"display": "13-inch Liquid Retina", "chip": "M4", "connector": "USB-C"},
     "compat": ["usb-c", "pencil-usb-c", "pencil-pro"]},
    {"product_id": "tb-pro11", "model": "iPad Pro 11-inch (M5)", "family": "iPad", "release_date": "2025-10-22",
     "colors": ["Space Black", "Silver"],
     "tiers": tiers((256, 999, True), (512, 1199, False), (1024, 1599, False), (2048, 1999, False)),
     "specs": {"display": "11-inch Ultra Retina XDR (tandem OLED)", "chip": "M5",
               "ram_gb": "12 (256/512 GB) or 16 (1/2 TB)", "connector": "Thunderbolt / USB 4 (40 Gb/s)",
               "wireless": "Wi-Fi 7"},
     "compat": ["usb-c", "pencil-usb-c", "pencil-pro"]},
    {"product_id": "tb-pro13", "model": "iPad Pro 13-inch (M5)", "family": "iPad", "release_date": "2025-10-22",
     "colors": ["Space Black", "Silver"],
     "tiers": tiers((256, 1299, False), (512, 1499, False), (1024, 1899, False), (2048, 2299, False)),
     "specs": {"display": "13-inch Ultra Retina XDR (tandem OLED)", "chip": "M5",
               "ram_gb": "12 (256/512 GB) or 16 (1/2 TB)", "connector": "Thunderbolt / USB 4 (40 Gb/s)",
               "wireless": "Wi-Fi 7"},
     "compat": ["usb-c", "pencil-usb-c", "pencil-pro"]},
]

LAPTOPS = [
    {"product_id": "lt-neo", "model": "MacBook Neo", "family": "MacBook", "release_date": "2026-03-11",
     "colors": ["Silver", "Blush", "Citrus", "Indigo"],
     "tiers": tiers((256, 699, True, 599, "2026-06-25"), (512, 799, True)),
     "specs": {"display": "13-inch Liquid Retina IPS, 2408 x 1506, 219 ppi, 500 nits",
               "chip": "A18 Pro (6-core CPU, 5-core GPU)", "memory_gb": 8, "battery_wh": 36.5,
               "ports": "1x USB-C 10 Gb/s (DisplayPort), 1x USB-C (USB 2), 3.5 mm headphone jack",
               "weight_kg": 1.22},
     "compat": ["usb-c"]},
    {"product_id": "lt-air13", "model": "MacBook Air 13-inch (M5)", "family": "MacBook", "release_date": "2026-03-04",
     "colors": ["Sky Blue", "Silver", "Starlight", "Midnight"],
     "tiers": tiers((512, 1299, True), (1024, 1499, False)),
     "specs": {"display": "13.6-inch Liquid Retina", "chip": "M5", "memory_gb": 16, "connector": "USB-C, MagSafe 3"},
     "compat": ["usb-c"]},
    {"product_id": "lt-air15", "model": "MacBook Air 15-inch (M5)", "family": "MacBook", "release_date": "2026-03-04",
     "colors": ["Sky Blue", "Silver", "Starlight", "Midnight"],
     "tiers": tiers((512, 1499, True), (1024, 1699, False)),
     "specs": {"display": "15.3-inch Liquid Retina", "chip": "M5", "memory_gb": 16, "connector": "USB-C, MagSafe 3"},
     "compat": ["usb-c"]},
    {"product_id": "lt-pro14", "model": "MacBook Pro 14-inch (M6)", "family": "MacBook", "release_date": "2026-11-06",
     "availability": "preorder",  # ships on release_date (ADR-043)
     "colors": ["Space Black", "Silver"],
     "tiers": tiers((1024, 1999, True), (2048, 2399, False)),
     "specs": {"display": "14-inch Liquid Retina XDR, 1600 nits HDR peak, nano-texture option",
               "chip": "M6 (12-core CPU, 12-core GPU)", "memory_gb": "16 (configurable to 32)",
               "battery": "up to 24 hours", "wireless": "Wi-Fi 7, Bluetooth 6",
               "ports": "3x Thunderbolt 4, HDMI, MagSafe 3, SDXC, headphone jack", "camera": "12 MP Center Stage"},
     "compat": ["usb-c"]},
    {"product_id": "lt-pro16", "model": "MacBook Pro 16-inch (M5 Pro)", "family": "MacBook", "release_date": "2026-03-04",
     "colors": ["Space Black", "Silver"],
     "tiers": tiers((1024, 2999, True)),
     "specs": {"display": "16-inch Liquid Retina XDR", "chip": "M5 Pro", "memory_gb": None,
               "ports": "Thunderbolt, HDMI, MagSafe 3, SDXC, headphone jack"},
     "compat": ["usb-c"]},
]


def watch(pid, model, rel, colors, sizes, specs, compat):
    return {"product_id": pid, "model": model, "family": "Watch", "release_date": rel, "colors": colors,
            "sizes": sizes, "specs": specs, "compat": compat}


WATCHES = [
    watch("wt-se3", "Watch SE 3", "2025-09-19", ["Midnight", "Starlight"],
          [("40mm", 249, True), ("44mm", 279, False)],
          {"case": "aluminum", "chip": None}, ["band:small", "band:large", "watch-charger"]),
    watch("wt-s12", "Watch Series 12", "2026-09-18", ["Jet Black", "Rose Gold", "Silver", "Space Gray"],
          [("42mm", 399, True), ("46mm", 429, False)],
          {"case": "aluminum (titanium and ceramic finishes also exist; not stocked)", "chip": "S11"},
          ["band:small", "band:large", "watch-charger"]),
    watch("wt-ultra4", "Watch Ultra 4", "2026-09-18", ["Natural Titanium", "Black Titanium"],
          [("49mm", 799, True)],
          {"case": "titanium", "battery": "up to 84 hours in Low Power Mode"},
          ["band:large", "watch-charger"]),
]

AUDIO = [
    {"product_id": "au-pods4", "model": "AirPods 4", "family": "AirPods", "release_date": "2024-09-20",
     "colors": ["White"], "price": 129, "specs": {"noise_cancellation": False, "case": "USB-C"},
     "compat": ["usb-c"]},
    {"product_id": "au-pods4anc", "model": "AirPods 4 with Active Noise Cancellation", "family": "AirPods",
     "release_date": "2024-09-20", "colors": ["White"], "price": 179,
     "specs": {"noise_cancellation": True, "case": "USB-C, wireless"}, "compat": ["usb-c", "qi2"]},
    {"product_id": "au-pro3", "model": "AirPods Pro 3", "family": "AirPods", "release_date": "2025-09-19",
     "colors": ["White"], "price": 249,
     "specs": {"noise_cancellation": True, "health": "heart-rate sensing", "case": "USB-C, MagSafe"},
     "compat": ["usb-c", "magsafe", "qi2"]},
    {"product_id": "au-max2", "model": "AirPods Max 2", "family": "AirPods", "release_date": "2026-04-01",
     "colors": ["Midnight", "Starlight", "Blue", "Purple", "Orange"], "price": 549,
     "specs": {"type": "over-ear", "chip": "H2", "connector": "USB-C"}, "compat": ["usb-c"]},
]

# Accessories: prices are realistic sample prices (price_verified false).
CASE_MODELS = ["ph-17e", "ph-16", "ph-17", "ph-air", "ph-18pro", "ph-18promax", "ph-duo"]
ACCESSORIES = []
names = {p["product_id"]: p["model"] for p in PHONES}
for pid in CASE_MODELS:
    ACCESSORIES.append({"product_id": f"ac-case-sil-{pid}", "model": f"Silicone Case with MagSafe for {names[pid]}",
                        "family": "Case", "price": 49, "colors": ["Black", "Stone", "Lake Green"],
                        "fits": [f"case:{pid}"], "note": f"Fits only {names[pid]}."})
    ACCESSORIES.append({"product_id": f"ac-case-clr-{pid}", "model": f"Clear Case with MagSafe for {names[pid]}",
                        "family": "Case", "price": 49, "colors": ["Clear"], "fits": [f"case:{pid}"],
                        "note": f"Fits only {names[pid]}."})
ACCESSORIES += [
    {"product_id": "ac-magsafe-1m", "model": "MagSafe Charger (1 m)", "family": "Charger", "price": 39,
     "fits": ["magsafe", "qi2"], "note": "Up to 25 W on supported phones with a 30 W+ adapter; Qi2 devices charge at lower power."},
    {"product_id": "ac-magsafe-2m", "model": "MagSafe Charger (2 m)", "family": "Charger", "price": 49,
     "fits": ["magsafe", "qi2"], "note": "Same as 1 m model, longer cable."},
    {"product_id": "ac-adapter-20w", "model": "20W USB-C Power Adapter", "family": "Power adapter", "price": 19,
     "fits": ["usb-c"], "note": "Charges any USB-C device; slower for laptops and 60 W phones."},
    {"product_id": "ac-adapter-40w", "model": "40W Dynamic Power Adapter with 60W Max", "family": "Power adapter",
     "price": 39, "fits": ["usb-c"], "note": "Enables fastest wired charging on phones that support 40-60 W."},
    {"product_id": "ac-cable-1m", "model": "USB-C Charge Cable (1 m)", "family": "Cable", "price": 19,
     "fits": ["usb-c"], "note": "USB-C to USB-C."},
    {"product_id": "ac-cable-240w", "model": "240W USB-C Charge Cable (2 m)", "family": "Cable", "price": 29,
     "fits": ["usb-c"], "note": "Supports laptop fast charging."},
    {"product_id": "ac-watch-charger", "model": "Watch Magnetic Fast Charger to USB-C Cable (1 m)",
     "family": "Charger", "price": 29, "fits": ["watch-charger"], "note": "For all stocked watches."},
    {"product_id": "ac-band-sport-s", "model": "Sport Band (fits 40mm and 42mm cases)", "family": "Watch band",
     "price": 49, "colors": ["Black", "Light Blush", "Denim"], "fits": ["band:small"],
     "note": "Fits 40 mm (SE 3) and 42 mm (Series 12) cases."},
    {"product_id": "ac-band-sport-l", "model": "Sport Band (fits 44mm, 46mm and 49mm cases)", "family": "Watch band",
     "price": 49, "colors": ["Black", "Light Blush", "Denim"], "fits": ["band:large"],
     "note": "Fits 44 mm (SE 3), 46 mm (Series 12) and 49 mm (Ultra 4) cases."},
    {"product_id": "ac-pencil-pro", "model": "Pencil Pro", "family": "Stylus", "price": 129,
     "fits": ["pencil-pro"], "note": "Works with iPad Pro (M5), iPad Air (M4) and iPad mini (A17 Pro); not with iPad (A16)."},
    {"product_id": "ac-pencil-usbc", "model": "Pencil (USB-C)", "family": "Stylus", "price": 79,
     "fits": ["pencil-usb-c"], "note": "Works with every stocked iPad."},
]


def sku(pid, *parts):
    return "-".join([pid.upper()] + [str(p).upper().replace(" ", "") for p in parts])


def device_products(items, category):
    out = []
    for p in items:
        variants = []
        if "tiers" in p:
            for t in p["tiers"]:
                for c in p["colors"]:
                    v = {"sku": sku(p["product_id"], f"{t['storage_gb']}GB", c), "storage_gb": t["storage_gb"],
                         "color": c, "list_price": t["list_price"], "price_verified": t["price_verified"]}
                    if "price_history" in t:
                        v["price_history"] = t["price_history"]
                    variants.append(v)
        elif "sizes" in p:
            for size, price, ver in p["sizes"]:
                for c in p["colors"]:
                    variants.append({"sku": sku(p["product_id"], size, c), "size": size, "color": c,
                                     "list_price": price, "price_verified": ver})
        else:
            for c in p["colors"]:
                variants.append({"sku": sku(p["product_id"], c), "color": c, "list_price": p["price"],
                                 "price_verified": True})
        out.append({"product_id": p["product_id"], "brand_id": BRAND, "category": category,
                    "family": p["family"], "model": p["model"], "release_date": p["release_date"],
                    "availability": p.get("availability", "available"), "specs_verified": SPECS_VERIFIED,
                    "specs": p["specs"], "compatibility_tags": p["compat"], "variants": variants,
                    "image": None})
    return out


def accessory_products():
    out = []
    for a in ACCESSORIES:
        colors = a.get("colors", ["Default"])
        out.append({"product_id": a["product_id"], "brand_id": BRAND, "category": "accessory",
                    "family": a["family"], "model": a["model"], "release_date": None, "availability": "available",
                    "specs_verified": SPECS_VERIFIED, "specs": {}, "fits_tags": a["fits"],
                    "compatibility_note": a["note"],
                    "variants": [{"sku": sku(a["product_id"], c), "color": c, "list_price": a["price"],
                                  "price_verified": False} for c in colors],
                    "image": None})
    return out


def compatibility(devices, accessories):
    """Derive device <-> accessory compatibility from tags (single source for check_compatibility)."""
    rows = []
    for acc in accessories:
        for dev in devices:
            if set(acc["fits_tags"]) & set(dev["compatibility_tags"]):
                rows.append({"accessory_id": acc["product_id"], "device_id": dev["product_id"],
                             "compatible": True, "note": acc["compatibility_note"]})
    return rows


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    cats = {"phones": device_products(PHONES, "phone"), "tablets": device_products(TABLETS, "tablet"),
            "laptops": device_products(LAPTOPS, "laptop"), "watches": device_products(WATCHES, "watch"),
            "audio": device_products(AUDIO, "audio"), "accessories": accessory_products()}
    for name, items in cats.items():
        (OUT / f"{name}.json").write_text(json.dumps(items, indent=2) + "\n")
    devices = [p for k, v in cats.items() if k != "accessories" for p in v]
    comp = compatibility(devices, cats["accessories"])
    (OUT / "compatibility.json").write_text(json.dumps(comp, indent=2) + "\n")
    n_var = sum(len(p["variants"]) for v in cats.values() for p in v)
    print(f"products={sum(len(v) for v in cats.values())} variants={n_var} compatibility_rows={len(comp)}")


if __name__ == "__main__":
    main()
