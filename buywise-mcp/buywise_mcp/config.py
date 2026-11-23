"""Settings from the environment (defaults = local Mac)."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    services_url: str = "http://localhost:8081"
    services_timeout_s: float = 10.0
    breaker_failures: int = 5  # consecutive failures that open the circuit (ADR-055)
    breaker_open_s: float = 10.0  # how long it stays open before one trial call


settings = Settings()
