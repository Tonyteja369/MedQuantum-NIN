from pathlib import Path
from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    environment: str = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    log_level: str = "INFO"
    max_upload_size_mb: int = 50
    allowed_origins: str = "http://localhost:5173"
    wfdb_sample_dir: str = "./data/samples"
    temp_dir: str = "./data/temp"
    model_version: str = "1.0.0"

    model_config = SettingsConfigDict(env_file=".env", protected_namespaces=("settings_",))

    @computed_field
    @property
    def allowed_origins_list(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]

    @computed_field
    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024

    def create_directories(self) -> None:
        Path(self.wfdb_sample_dir).mkdir(parents=True, exist_ok=True)
        Path(self.temp_dir).mkdir(parents=True, exist_ok=True)


settings = Settings()
