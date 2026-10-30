"""Settings from environment (.env.example lists them). All model calls go through LiteLLM (ADR-026)."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    llm_gateway_url: str = "http://localhost:4000"
    litellm_master_key: str = "sk-buywise-local"
    llm_primary_model: str = "buywise-primary"
    embed_model: str = "bge-m3"
    database_url: str = "postgresql://agent:agent-local@localhost:5432/agent"
    redis_url: str = "redis://localhost:6379/0"
    mcp_url: str = "http://localhost:8090/mcp"
    services_url: str = "http://localhost:8081"
    knowledge_dir: str = "../data/knowledge"


settings = Settings()
