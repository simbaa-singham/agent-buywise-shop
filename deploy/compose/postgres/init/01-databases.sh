#!/bin/bash
# One database and one user per deployable/tool; each user can access only its own database (ADR-010).
set -euo pipefail

create_db() {
  local db=$1 user=$2 password=$3
  psql -v ON_ERROR_STOP=1 --username postgres <<SQL
CREATE USER ${user} WITH PASSWORD '${password}';
CREATE DATABASE ${db} OWNER ${user};
REVOKE ALL ON DATABASE ${db} FROM PUBLIC;
SQL
}

create_db services services "${SERVICES_DB_PASSWORD}"
create_db agent    agent    "${AGENT_DB_PASSWORD}"
create_db keycloak keycloak "${KEYCLOAK_DB_PASSWORD}"
create_db litellm  litellm  "${LITELLM_DB_PASSWORD}"

# pgvector for the knowledge schema in the agent database (ADR-011, ADR-040)
psql -v ON_ERROR_STOP=1 --username postgres --dbname agent -c "CREATE EXTENSION IF NOT EXISTS vector;"
