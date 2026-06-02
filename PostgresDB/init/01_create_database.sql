SELECT 'CREATE DATABASE fastapi_ms'
WHERE NOT EXISTS (
    SELECT FROM pg_database WHERE datname = 'fastapi_ms'
)\gexec

\connect fastapi_ms