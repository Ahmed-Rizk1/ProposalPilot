import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_ENV: str = "development"
    DATABASE_URL: str = "sqlite:///./proposalpilot.db"
    GROQ_API_KEY: str = ""
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    JWT_SECRET: str = "dev-secret-key-proposalpilot-2026"
    JWT_ALGORITHM: str = "HS256"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()

def validate_config():
    if not settings.GROQ_API_KEY:
        print("[WARNING] GROQ_API_KEY is not set in .env. LLM proposal generation will use mock responses.")
