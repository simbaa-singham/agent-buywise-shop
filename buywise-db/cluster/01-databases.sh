#!/bin/bash
# One database and one user per deployable/tool; each user can access only its own database (ADR-010).
# Runs ONCE, on the first start of the Postgres container (empty data folder): the image runs every script in
# /docker-entrypoint-initdb.d, and compose.yaml mounts this folder there (read-only). Later starts skip it.
# Passwords arrive as environment variables set in compose.yaml from deploy/compose/.env.
set -euo pipefail                 # stop on the first error (-e), on an unset variable (-u), and if any command in a pipe fails

create_db() {                     # creates one user + one database; called once per database below
  local db=$1 user=$2 password=$3 # inputs: database name, user name, password
  # run the SQL below as the admin user (postgres); ON_ERROR_STOP=1 = stop at the first SQL error
  psql -v ON_ERROR_STOP=1 --username postgres <<SQL
-- 1. a login user just for this database
CREATE USER ${user} WITH PASSWORD '${password}';
-- 2. the database, owned by that user: the owner can create schemas and tables inside it (Flyway, agent ingest)
CREATE DATABASE ${db} OWNER ${user};
-- 3. PUBLIC = every user; by default any user may connect to any database - remove that, so only the owner can
REVOKE ALL ON DATABASE ${db} FROM PUBLIC;
SQL
}

create_db services services "${SERVICES_DB_PASSWORD}"   # buywise-services: catalog, inventory, customers, orders
create_db agent    agent    "${AGENT_DB_PASSWORD}"      # buywise-agent: agent data + RAG chunks with vectors
create_db keycloak keycloak "${KEYCLOAK_DB_PASSWORD}"   # Keycloak's own tables (users, realm settings)
create_db litellm  litellm  "${LITELLM_DB_PASSWORD}"    # LiteLLM spend records

# pgvector for the knowledge schema in the agent database (ADR-011, ADR-040).
# Turning on an extension needs the admin (superuser); the agent user is not one, so it is done here, once,
# and only in the agent database - the others do not need vectors.
psql -v ON_ERROR_STOP=1 --username postgres --dbname agent -c "CREATE EXTENSION IF NOT EXISTS vector;"
