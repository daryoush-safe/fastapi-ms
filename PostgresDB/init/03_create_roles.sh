#!/bin/bash
set -euo pipefail

: "${USER_SERVICE_DB_PASSWORD:?USER_SERVICE_DB_PASSWORD must be set}"
: "${SUBSCRIPTION_SERVICE_DB_PASSWORD:?SUBSCRIPTION_SERVICE_DB_PASSWORD must be set}"
: "${DEBEZIUM_DB_PASSWORD:?DEBEZIUM_DB_PASSWORD must be set}"

psql -v ON_ERROR_STOP=1 \
  --username "$POSTGRES_USER" \
  --dbname fastapi_ms \
  -v user_pass="$USER_SERVICE_DB_PASSWORD" \
  -v sub_pass="$SUBSCRIPTION_SERVICE_DB_PASSWORD" \
  -v dbz_pass="$DEBEZIUM_DB_PASSWORD" <<'SQL'
CREATE ROLE user_service_role          WITH LOGIN PASSWORD :'user_pass' REPLICATION;
CREATE ROLE subscription_service_role  WITH LOGIN PASSWORD :'sub_pass'  REPLICATION;
CREATE ROLE debezium_role              WITH LOGIN PASSWORD :'dbz_pass'  REPLICATION;
SQL
