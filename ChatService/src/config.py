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

    # Auth (JWT)
    jwt_secret: str = Field(..., alias="JWT_SECRET")
    jwt_algorithm: str = Field("HS256", alias="JWT_ALGORITHM")

    # Kafka
    kafka_bootstrap_servers: str = Field("kafka:29092", alias="KAFKA_BOOTSTRAP_SERVERS")

    # DBService
    dbservice_url: str = Field("http://db-service:8003", alias="DBSERVICE_URL")
    dbservice_timeout: float = Field(10.0, alias="DBSERVICE_TIMEOUT")

    # ML service
    mlservice_url: str = Field("http://inference-api:8080", alias="MLSERVICE_URL")
    mlservice_stream_path: str = Field("/stream-query", alias="MLSERVICE_STREAM_PATH")
    mlservice_timeout: float = Field(120.0, alias="MLSERVICE_TIMEOUT")

    # App
    app_name: str = Field("ChatService", alias="APP_NAME")
    app_host: str = Field("0.0.0.0", alias="APP_HOST")
    app_port: int = Field(8004, alias="APP_PORT")
    debug: bool = Field(False, alias="DEBUG")
    root_path: str = Field("chat", alias="ROOT_PATH")

    # CORS
    cors_origins: str = Field("http://localhost:3000", alias="CORS_ORIGINS")

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore
