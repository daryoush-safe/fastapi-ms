#!/bin/sh
set -e

wait_for() {
  HOST=$1
  PORT=$2
  NAME=$3
  echo "Waiting for $NAME at $HOST:$PORT..."
  while ! nc -z "$HOST" "$PORT" 2>/dev/null; do
    sleep 2
  done
  echo "$NAME is ready."
}

# nc is available in python:3.12-slim via netcat-openbsd — install it at build time
# These env vars come from docker-compose
wait_for "${DB_HOST:-postgres}"    "${DB_PORT:-5432}"   "PostgreSQL"
wait_for "${KAFKA_HOST:-kafka}"    "${KAFKA_PORT:-29092}" "Kafka"