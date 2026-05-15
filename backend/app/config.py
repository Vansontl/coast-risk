from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    app_name: str = "CoastalRisk WebApp API"
    app_env: str = "development"
    api_host: str = "127.0.0.1"
    api_port: int = 8010
    database_url: str = "postgresql+psycopg://postgres:postgres@127.0.0.1:5432/coastalrisk_webapp_v1"
    storage_dir: str = "./storage"
    model_dir: str = "./storage/models"
    report_dir: str = "./storage/reports"
    upload_dir: str = "./storage/uploads"
    cors_origins: str = "http://127.0.0.1:3010,http://localhost:3010"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> List[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]


settings = Settings()
