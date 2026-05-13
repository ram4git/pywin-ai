# win-auto/backend/config.py
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-20250514"
    server_host: str = "0.0.0.0"
    server_port: int = 8000
    database_url: str = "sqlite:///data/win-auto.db"
    screenshots_dir: str = "data/screenshots"
    scripts_dir: str = "data/scripts"
    execution_timeout_seconds: int = 300
    screenshot_retention_days: int = 30
    log_file: str = "data/win-auto.log"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

settings = Settings()
