#!/usr/bin/env bash
set -euo pipefail

CONNECT_URL="${KAFKA_CONNECT_URL:-http://kafka-connect:8083}"
CONNECTORS_DIR="/debezium/connectors"

wait_for_connect() {
  echo "Waiting for Kafka Connect at ${CONNECT_URL}…"
  until curl -sf "${CONNECT_URL}/connectors" > /dev/null; do
    sleep 3
  done
  echo "Kafka Connect is ready."
}

register_connector() {
  local file="$1"
  local payload
  # substitute only DB_* vars; leave Debezium expressions like ${routedByValue} intact
  payload=$(envsubst '${DB_HOST} ${DB_PORT} ${DB_USER} ${DB_PASSWORD} ${DB_NAME}' < "$file")

  local name
  name=$(echo "$payload" | python3 -c "import json,sys; print(json.load(sys.stdin)['name'])")

  echo "Registering connector: ${name}"

  local response http_code
  if curl -sf "${CONNECT_URL}/connectors/${name}" > /dev/null 2>&1; then
    echo "  → already registered, updating…"
    response=$(curl -s -o /tmp/curl_body -w "%{http_code}" -X PUT \
      -H "Content-Type: application/json" \
      --data "$payload" \
      "${CONNECT_URL}/connectors/${name}/config")
  else
    echo "  → creating…"
    response=$(curl -s -o /tmp/curl_body -w "%{http_code}" -X POST \
      -H "Content-Type: application/json" \
      --data "$payload" \
      "${CONNECT_URL}/connectors")
  fi

  http_code="$response"
  if [ "$http_code" -ge 400 ]; then
    echo "  ✗ failed (HTTP ${http_code}):"
    cat /tmp/curl_body
    exit 1
  fi

  echo "  ✓ ${name} registered (HTTP ${http_code})."
}

wait_for_connect

for connector_file in "${CONNECTORS_DIR}"/*.json; do
  register_connector "$connector_file"
done

echo "All connectors registered."
