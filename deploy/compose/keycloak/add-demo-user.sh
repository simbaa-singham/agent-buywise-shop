#!/usr/bin/env bash
# Local only: sets the customer-web client secret and creates the demo customer login on a running Keycloak.
# The login email matches seed customer cu-demo (customer.demo@example.com); password from compose/.env.
set -euo pipefail
source "$(dirname "$0")/../.env"
k() { docker exec buywise-keycloak-1 /opt/keycloak/bin/kcadm.sh "$@"; }
k config credentials --server http://localhost:8080 --realm master --user admin --password "$KEYCLOAK_ADMIN_PASSWORD"
cid=$(k get clients -r buywise -q clientId=buywise-customer-web --fields id --format csv --noquotes)
k update "clients/$cid" -r buywise -s "secret=$CUSTOMER_WEB_CLIENT_SECRET"
if [ -z "$(k get users -r buywise -q email=customer.demo@example.com --fields id --format csv --noquotes)" ]; then
  k create users -r buywise -s username=demo -s email=customer.demo@example.com -s emailVerified=true \
    -s firstName=Demo -s lastName=Customer -s enabled=true
fi
k set-password -r buywise --username demo --new-password "$DEMO_CUSTOMER_PASSWORD"
echo "demo login ready: username demo (password in deploy/compose/.env)"
