from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", populate_by_name=True)

    api_key: str = Field(default="audit_demo_key", validation_alias=AliasChoices("AUDIT_API_KEY", "API_KEY"))
    database_url: str = Field(
        default="sqlite:///./data/audit.db",
        validation_alias=AliasChoices("DATABASE_URL"),
    )
    retention_days: int = 30
    cors_origins: str = Field(
        default="http://localhost:5173,http://127.0.0.1:5173",
        validation_alias=AliasChoices("CORS_ORIGINS", "cors_origins"),
    )


settings = Settings()
