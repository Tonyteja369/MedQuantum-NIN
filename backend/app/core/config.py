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
    ml_model_path: str = "./backend/app/models/ml_weights.json"
    enable_rule_engine: bool = True
    enable_ml: bool = True
    enable_probabilistic: bool = True
    fusion_weight_rule: float = 0.5
    fusion_weight_ml: float = 0.3
    fusion_weight_prob: float = 0.2
    max_signal_duration_sec: int = 30
    max_leads: int = 12
    performance_budget_ms: int = 3000

    model_config = SettingsConfigDict(env_file=".env", protected_namespaces=("settings_",))

    @computed_field
    @property
    def allowed_origins_list(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]

    @computed_field
    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024

    @computed_field
    @property
    def fusion_weights(self) -> dict[str, float]:
        weights = {
            "rule": max(self.fusion_weight_rule, 0.0),
            "ml": max(self.fusion_weight_ml, 0.0),
            "prob": max(self.fusion_weight_prob, 0.0),
        }
        total = sum(weights.values()) or 1.0
        return {k: v / total for k, v in weights.items()}

    def create_directories(self) -> None:
        Path(self.wfdb_sample_dir).mkdir(parents=True, exist_ok=True)
        Path(self.temp_dir).mkdir(parents=True, exist_ok=True)


settings = Settings()
