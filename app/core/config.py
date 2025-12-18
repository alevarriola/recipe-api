from pydantic_settings import BaseSettings, SettingsConfigDict

# Application settings
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite+aiosqlite:///./recipes.db"

    # Anthropic  API settings
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-3-5-sonnet-latest"

# Instantiate settings
settings = Settings()
