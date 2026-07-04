from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    openrouter_api_key: Optional[str] = None
    openrouter_model: Optional[str] = "openrouter/auto"
    kubeconfig_path: Optional[str] = None

    class Config:
        env_file = ".env"

settings = Settings()
