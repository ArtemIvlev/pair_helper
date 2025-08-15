from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl


class Settings(BaseSettings):
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Пульс ваших отношений"
    
    # CORS - только разрешенные домены
    ALLOWED_HOSTS: List[str] = [
        "https://gallery.homoludens.photos",
        "gallery.homoludens.photos",  # Для API запросов через nginx
        "https://gallery-dev.homoludens.photos",
        "gallery-dev.homoludens.photos",  # Для dev API запросов через nginx
        "https://t.me", 
        "https://web.telegram.org",
        "192.168.2.*",         # Вся подсеть сервера
        "172.16.*.*",          # Docker внутренние сети
        "172.17.*.*",          # Docker bridge сети
        "172.18.*.*",          # Docker compose сети
        "10.*.*.*",            # Внутренние сети
        "localhost",           # Локальные запросы
        "127.0.0.1"            # Loopback
    ]
    
    # Database
    DATABASE_URL: str = "postgresql://pair_user:pair_password@localhost:5432/pair_helper"
    
    # Security
    SECRET_KEY: str = "your-super-secret-key-change-this-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_WEBAPP_URL: str = ""
    
    # Application
    DEBUG: bool = True
    
    # Optional variables (for compatibility)
    API_BASE_URL: str = "http://localhost:8000"
    VITE_API_BASE_URL: str = "http://localhost:8000"

    # Analytics
    ANALYTICS_ENABLED: bool = True
    
    # Anthropic API
    ANTHROPIC_API_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Игнорировать дополнительные переменные


settings = Settings()
