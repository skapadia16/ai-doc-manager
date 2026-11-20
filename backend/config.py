# =====================================================
# config.py — Saari settings ek jagah
# =====================================================
# .env file se settings load karta hai
# Poore app mein "settings" object use hoga

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # JWT
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Hugging Face
    HF_TOKEN: str
    HF_MODEL: str = "Qwen/Qwen2.5-7B-Instruct"

    # File Upload
    MAX_FILE_SIZE: int = 52428800  # 50MB
    UPLOAD_DIR: str = "uploads"
    VECTOR_DB_DIR: str = "vector_db"

    class Config:
        env_file = ".env"  # .env file se values load karo

# Ek baar banao, poore app mein import karo
settings = Settings()
