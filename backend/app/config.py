from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "POLARIS"
    app_version: str = "0.5.0"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5433/polaris"
    api_prefix: str = "/api"
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    jwt_secret: str = "change-me-in-production"
    demo_mode_label: str = "SYNTHETIC DEMONSTRATION DATA"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def cors_allowlist(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
