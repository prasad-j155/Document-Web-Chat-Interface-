# app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    redis_host: str = "localhost"
    redis_port: int = 6379
    groq_api_key: str = ""  # <--- This is the exact variable it was looking for!

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()