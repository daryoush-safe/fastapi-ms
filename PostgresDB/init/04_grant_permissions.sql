\connect fastapi_ms

-- ─── Database level access ────────────────────────────────────────────────────
-- These are required for CREATE PUBLICATION to work
GRANT CREATE ON DATABASE fastapi_ms TO user_service_role;
GRANT CREATE ON DATABASE fastapi_ms TO subscription_service_role;
GRANT CREATE ON DATABASE fastapi_ms TO debezium_role;

-- ─── Schema access ────────────────────────────────────────────────────────────
GRANT USAGE, CREATE ON SCHEMA auth TO user_service_role;
GRANT USAGE, CREATE ON SCHEMA auth TO subscription_service_role;
GRANT USAGE ON SCHEMA auth TO debezium_role;

-- ─── Future table grants (applied to tables created by each service role) ─────
-- Each service role automatically owns the tables it creates via Alembic.
-- Grant debezium_role SELECT on any tables those roles create.
ALTER DEFAULT PRIVILEGES FOR ROLE user_service_role IN SCHEMA auth
    GRANT SELECT ON TABLES TO debezium_role;

ALTER DEFAULT PRIVILEGES FOR ROLE subscription_service_role IN SCHEMA auth
    GRANT SELECT ON TABLES TO debezium_role;

-- ─── Debezium: allow creating publications ────────────────────────────────────
GRANT CREATE ON DATABASE fastapi_ms TO debezium_role;
