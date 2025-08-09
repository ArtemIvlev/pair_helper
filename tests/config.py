import os
from dotenv import load_dotenv

load_dotenv()

class TestConfig:
    # API URLs
    API_BASE_URL = os.getenv("API_BASE_URL", "http://192.168.2.228:8000/api")
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://192.168.2.228:3000")
    
    # Portainer API
    PORTAINER_URL = "https://192.168.2.228:31015"
    PORTAINER_USERNAME = os.getenv("PORTAINER_USERNAME", "admin")
    PORTAINER_PASSWORD = os.getenv("PORTAINER_PASSWORD", "admin")
    
    # Если логин/пароль не указаны, выводим предупреждение
    @classmethod
    def validate_credentials(cls):
        if cls.PORTAINER_USERNAME == "admin" and cls.PORTAINER_PASSWORD == "admin":
            print("⚠️  ВНИМАНИЕ: Используются дефолтные логин/пароль для Portainer!")
            print("   Установите переменные окружения:")
            print("   export PORTAINER_USERNAME=your_username")
            print("   export PORTAINER_PASSWORD=your_password")
            print("   или добавьте их в файл .env")
            return False
        return True
    
    # Test data
    TEST_TELEGRAM_ID = 123456789
    TEST_USER_FIRST_NAME = "Test User"
    
    # Container names
    CONTAINERS = {
        "backend": "pair-helper-backend",
        "frontend": "pair-helper-frontend", 
        "bot": "pair-helper-bot",
        "admin": "pair-helper-admin"
    }
    
    # Expected endpoints
    ENDPOINTS = {
        "health": "/health",
        "docs": "/docs",
        "users": "/v1/users",
        "invitations": "/v1/invitations"
    }
