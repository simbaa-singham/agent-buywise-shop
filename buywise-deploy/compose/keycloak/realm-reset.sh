#!/usr/bin/env bash
# Local only: re-creates the buywise realm from buywise-realm.json (ADR-050 amendment). Keycloak imports the realm
# file only when the realm does not exist, so: delete it, restart Keycloak (re-import), then add the local secrets
# and the demo login again. All buywise logins and sessions are lost - fine locally, never do this in production.
set -euo pipefail
cd "$(dirname "$0")/.."
source .env
docker exec buywise-keycloak-1 /opt/keycloak/bin/kcadm.sh config credentials --server http://localhost:8080 \
  --realm master --user admin --password "$KEYCLOAK_ADMIN_PASSWORD"
docker exec buywise-keycloak-1 /opt/keycloak/bin/kcadm.sh delete realms/buywise || true
docker compose -f compose.yaml --env-file .env restart keycloak
for _ in $(seq 1 60); do
  curl -sf http://localhost:8080/realms/buywise >/dev/null && break
  sleep 2
done
curl -sf http://localhost:8080/realms/buywise >/dev/null || { echo "Keycloak did not come back"; exit 1; }
./keycloak/add-demo-user.sh
