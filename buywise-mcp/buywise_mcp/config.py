"""Settings from the environment (defaults = local Mac)."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    services_url: str = "http://localhost:8081"
    public_url: str = "http://localhost:8090"  # how clients reach MCP; base of each server's resource URL

    # OAuth (ADR-050): tokens must come from this issuer and be for this audience
    issuer: str = "http://localhost:8080/realms/buywise"
    jwks_url: str = ""  # empty = issuer + /protocol/openid-connect/certs (set when MCP reaches Keycloak differently)
    audience: str = "buywise-mcp"
    client_id: str = "buywise-mcp"  # MCP's own Keycloak client: swaps tokens for buywise-services
    client_secret: str = "mcp-local-secret"
    services_audience: str = "buywise-services"
    services_timeout_s: float = 10.0
    breaker_failures: int = 5  # consecutive failures that open the circuit (ADR-055)
    breaker_open_s: float = 10.0  # how long it stays open before one trial call

    @property
    def jwks(self) -> str:
        return self.jwks_url or f"{self.issuer}/protocol/openid-connect/certs"

    @property
    def token_url(self) -> str:
        return f"{self.issuer}/protocol/openid-connect/token"


settings = Settings()  # read at call time (not import time), so tests can point it at their containers
