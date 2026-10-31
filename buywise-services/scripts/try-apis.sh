#!/usr/bin/env bash
# Try the buywise-services APIs one by one. Needs the app running (make -C buywise-services run, or make start).
# Run all:  ./buywise-services/scripts/try-apis.sh      or copy single commands into the terminal.
B=localhost:8081
pp() { python3 -m json.tool | head -${1:-25}; echo; }

echo "== 1. Search products: 'iphone 18 pro'"
curl -s "$B/api/products?q=iphone+18+pro&limit=3" | pp

echo "== 2. One product with every variant (SKU) and price"
curl -s "$B/api/products/ph-18pro" | pp 30

echo "== 3. All stores"
curl -s "$B/api/stores" | pp 15

echo "== 4. Stock of one SKU at Austin"
curl -s "$B/api/stock?skus=PH-18PRO-256GB-SILVER&storeId=st-aus" | pp

echo "== 5. Stock of one SKU at every store"
curl -s "$B/api/stock?skus=PH-18PRO-256GB-SILVER" | pp 40

echo "== 6. Find a customer by email (what login does)"
curl -s "$B/api/customers?email=customer.demo@example.com" | pp

echo "== 7. Demo customer's latest 2 orders"
curl -s -H 'X-Customer-Id: cu-demo' "$B/api/orders?limit=2" | pp 40

echo "== 8. Quote: price an order, nothing saved"
curl -s -X POST -H 'X-Customer-Id: cu-demo' -H 'Content-Type: application/json' "$B/api/orders/quote" \
  -d '{"items":[{"sku":"PH-18PRO-256GB-SILVER","quantity":1}],"fulfilment":"pickup","storeId":"st-aus"}' | pp 30

echo "== 9. Another customer asks for demo's order -> 404"
curl -s -H 'X-Customer-Id: cu-0002' "$B/api/orders/BW-200004" | pp

echo "== 10. Bad request: unknown SKU -> 400 with a clear message"
curl -s -X POST -H 'X-Customer-Id: cu-demo' -H 'Content-Type: application/json' "$B/api/orders/quote" \
  -d '{"items":[{"sku":"NOPE-123","quantity":1}],"fulfilment":"pickup","storeId":"st-aus"}' | pp

echo "== 11. Health"
curl -s "$B/actuator/health"; echo
