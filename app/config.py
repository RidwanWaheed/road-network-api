import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    API_TITLE: str = os.getenv("API_TITLE", "Road Network API")
    API_VERSION: str = os.getenv("API_VERSION", "0.1.0")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/roadnetworkdb")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    class Config:
        env_file = ".env"

settings = Settings()


