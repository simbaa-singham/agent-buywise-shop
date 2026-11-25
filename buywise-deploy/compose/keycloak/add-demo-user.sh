#!/usr/bin/env bash
# Local only: sets the Keycloak client secrets and creates the demo customer login on a running Keycloak.
# Secrets and passwords come from compose/.env (never from the realm file in git). Safe to run again.
# The demo login carries customer_id=cu-demo (seed customer, customer.demo@example.com) as a token claim (ADR-050);
# the customer role comes from the realm's default role.
set -euo pipefail
source "$(dirname "$0")/../.env"
k() { docker exec buywise-keycloak-1 /opt/keycloak/bin/kcadm.sh "$@"; }
k config credentials --server http://localhost:8080 --realm master --user admin --password "$KEYCLOAK_ADMIN_PASSWORD"

secret() {  # client id, secret
  local cid
  cid=$(k get clients -r buywise -q clientId="$1" --fields id --format csv --noquotes)
  k update "clients/$cid" -r buywise -s "secret=$2"
}
secret buywise-customer-web "$CUSTOMER_WEB_CLIENT_SECRET"
secret buywise-agent "$AGENT_CLIENT_SECRET"
secret buywise-mcp "$MCP_CLIENT_SECRET"

if [ -z "$(k get users -r buywise -q email=customer.demo@example.com --fields id --format csv --noquotes)" ]; then
  k create users -r buywise -s username=demo -s email=customer.demo@example.com -s emailVerified=true \
    -s firstName=Demo -s lastName=Customer -s enabled=true -s 'attributes.customer_id=["cu-demo"]'
fi
uid=$(k get users -r buywise -q username=demo --fields id --format csv --noquotes)
k update "users/$uid" -r buywise -s 'attributes.customer_id=["cu-demo"]' -s firstName=Demo -s lastName=Customer \
  -s email=customer.demo@example.com -s emailVerified=true
k set-password -r buywise --username demo --new-password "$DEMO_CUSTOMER_PASSWORD"
echo "demo login ready: username demo (password in buywise-deploy/compose/.env), customer_id cu-demo"
