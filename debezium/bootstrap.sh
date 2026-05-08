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
  local name
  name=$(python3 -c "import json,sys; print(json.load(sys.stdin)['name'])" < "$file")

  echo "Registering connector: ${name}"

  # Check if already exists
  if curl -sf "${CONNECT_URL}/connectors/${name}" > /dev/null 2>&1; then
    echo "  → already registered, updating…"
    curl -sf -X PUT \
      -H "Content-Type: application/json" \
      --data @"$file" \
      "${CONNECT_URL}/connectors/${name}/config" | python3 -m json.tool
  else
    echo "  → creating…"
    curl -sf -X POST \
      -H "Content-Type: application/json" \
      --data @"$file" \
      "${CONNECT_URL}/connectors" | python3 -m json.tool
  fi

  echo "  ✓ ${name} registered."
}

wait_for_connect

for connector_file in "${CONNECTORS_DIR}"/*.json; do
  register_connector "$connector_file"
done

echo "All connectors registered."