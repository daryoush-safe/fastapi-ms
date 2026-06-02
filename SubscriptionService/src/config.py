from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Database
    database_url: str = Field(..., alias="DATABASE_URL")
    db_echo: bool = Field(False, alias="DB_ECHO")
    db_pool_size: int = Field(5, alias="DB_POOL_SIZE")
    db_max_overflow: int = Field(10, alias="DB_MAX_OVERFLOW")

    # Stripe
    stripe_secret_key: str = Field(..., alias="STRIPE_SECRET_KEY")
    stripe_webhook_secret: str = Field(..., alias="STRIPE_WEBHOOK_SECRET")
    stripe_success_url: str = Field(
        "http://localhost:3000/success", alias="STRIPE_SUCCESS_URL"
    )
    stripe_cancel_url: str = Field(
        "http://localhost:3000/cancel", alias="STRIPE_CANCEL_URL"
    )

    # Kafka
    kafka_bootstrap_servers: str = Field("kafka:29092", alias="KAFKA_BOOTSTRAP_SERVERS")

    # App
    app_name: str = Field("SubscriptionService", alias="APP_NAME")
    app_host: str = Field("0.0.0.0", alias="APP_HOST")
    app_port: int = Field(8000, alias="APP_PORT")
    debug: bool = Field(False, alias="DEBUG")

    # CORS — comma-separated list of allowed origins. Never use "*" together with
    # credentialed requests; list the exact frontend origins instead.
    cors_origins: str = Field("http://localhost:3000", alias="CORS_ORIGINS")

    # Auth (JWT). This service only *verifies* tokens minted by UserService, so the
    # secret/algorithm must match UserService exactly.
    jwt_secret: str = Field(..., alias="JWT_SECRET")
    jwt_algorithm: str = Field("HS256", alias="JWT_ALGORITHM")

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore
