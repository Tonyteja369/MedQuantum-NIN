from pathlib import Path

from pydantic import computed_field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application configuration with Vercel deployment support.

    CORS Configuration:
    - allowed_origins: list[str] of CORS-allowed origins
    - NEVER use allowed_origin_regex or parse origins at runtime
    - NEVER access undefined attributes like allowed_origins_list
    - Always parse origins once in config using field_validator and model_validator
    - For Vercel monorepo: use allowed_origins=['*'] (same domain in production)
    - For environment override: set ALLOWED_ORIGINS env var as comma-separated string
    """

    environment: str = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    log_level: str = "INFO"
    max_upload_size_mb: int = 50
    frontend_url: str = ""
    allowed_origins: list[str] = ["*"]
    wfdb_sample_dir: str = "/tmp/medquantum/samples"
    temp_dir: str = "/tmp/medquantum/temp"
    model_version: str = "1.0.0"

    model_config = SettingsConfigDict(env_file=".env", protected_namespaces=("settings_",))

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, value):
        """Parse allowed_origins from various input types to list[str]."""
        if value is None:
            return ["*"]

        if isinstance(value, str):
            origins = [origin.strip() for origin in value.split(",") if origin.strip()]
            return origins or ["*"]

        if isinstance(value, (list, tuple, set)):
            origins = [str(origin).strip() for origin in value if str(origin).strip()]
            return origins or ["*"]

        return ["*"]

    @model_validator(mode="after")
    def add_frontend_url(self):
        """Add frontend_url to allowed_origins if not wildcard."""
        if self.frontend_url and "*" not in self.allowed_origins and self.frontend_url not in self.allowed_origins:
            self.allowed_origins.append(self.frontend_url)
        return self

    @computed_field
    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024

    def create_directories(self) -> None:
        Path(self.wfdb_sample_dir).mkdir(parents=True, exist_ok=True)
        Path(self.temp_dir).mkdir(parents=True, exist_ok=True)
    environment: str = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    log_level: str = "INFO"
    max_upload_size_mb: int = 50
    frontend_url: str = ""
    allowed_origins: list[str] = ["*"]
    wfdb_sample_dir: str = "/tmp/medquantum/samples"
    temp_dir: str = "/tmp/medquantum/temp"
    model_version: str = "1.0.0"

    model_config = SettingsConfigDict(env_file=".env", protected_namespaces=("settings_",))

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, value):
        if value is None:
            return ["*"]

        if isinstance(value, str):
            origins = [origin.strip() for origin in value.split(",") if origin.strip()]
            return origins or ["*"]

        if isinstance(value, (list, tuple, set)):
            origins = [str(origin).strip() for origin in value if str(origin).strip()]
            return origins or ["*"]

        return ["*"]

    @model_validator(mode="after")
    def add_frontend_url(self):
        if self.frontend_url and "*" not in self.allowed_origins and self.frontend_url not in self.allowed_origins:
            self.allowed_origins.append(self.frontend_url)
        return self

    @computed_field
    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024

    def create_directories(self) -> None:
        Path(self.wfdb_sample_dir).mkdir(parents=True, exist_ok=True)
        Path(self.temp_dir).mkdir(parents=True, exist_ok=True)


settings = Settings()
