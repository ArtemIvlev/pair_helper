import os
import logging
import fnmatch
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.api.api_v1.api import api_router
from app.core.database import engine
from app.models import Base
from app.middleware.security import RateLimitMiddleware, SecurityHeadersMiddleware, TelegramValidationMiddleware, ProxyHeadersMiddleware
from app.middleware.usage_analytics import UsageAnalyticsMiddleware
from app.notifications import rules as _notification_rules  # noqa: F401
from app.notifications.engine import NotificationEngine

# Информация о билде
BUILD_DATE = os.getenv("BUILD_DATE", "unknown")
BUILD_ID = os.getenv("BUILD_ID", "unknown") 
BUILD_MARKER = os.getenv("BUILD_MARKER", "unknown")

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Кастомный middleware для проверки хостов с поддержкой wildcards
class CustomTrustedHostMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, allowed_hosts):
        super().__init__(app)
        self.allowed_hosts = allowed_hosts

    async def dispatch(self, request: Request, call_next):
        host = request.headers.get("host", "")
        
        # Проверяем разрешенные хосты
        if self._is_host_allowed(host):
            return await call_next(request)
        
        # Логируем отклоненный хост для отладки
        logger.warning(f"Host not allowed: {host}")
        raise HTTPException(status_code=400, detail="Invalid host header")
    
    def _is_host_allowed(self, host: str) -> bool:
        for allowed_host in self.allowed_hosts:
            # Убираем протокол из allowed_host если есть
            clean_allowed = allowed_host.replace("https://", "").replace("http://", "")
            
            # Проверка с wildcards
            if fnmatch.fnmatch(host, clean_allowed):
                return True
            
            # Точное совпадение
            if host == clean_allowed:
                return True
        
        return False

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Пульс ваших отношений API",
    description="API для Telegram Web App для пар",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Настройка для работы за прокси (nginx) - кастомный middleware с поддержкой wildcards
app.add_middleware(
    CustomTrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted hosts middleware уже добавлен выше

# Security middlewares (порядок важен!)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(ProxyHeadersMiddleware)  # Первым - для правильного получения IP
app.add_middleware(RateLimitMiddleware, calls=100, period=60)  # 100 запросов в минуту
app.add_middleware(TelegramValidationMiddleware)
app.add_middleware(UsageAnalyticsMiddleware)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_event():
    """Событие при запуске приложения"""
    logger.info(f"🚀 Пульс ваших отношений Backend запущен!")
    logger.info(f"📦 Build ID: {BUILD_ID}")
    logger.info(f"📅 Build Date: {BUILD_DATE}")
    logger.info(f"🏷️  {BUILD_MARKER}")
    # Аналитика на Postgres не требует специальной инициализации
    
    # Инициализация движка уведомлений (правила регистрируются при импорте)
    app.state.notification_engine = NotificationEngine()

@app.get("/")
async def root():
    return {
        "message": "Пульс ваших отношений API", 
        "version": "1.0.0",
        "build_id": BUILD_ID,
        "build_date": BUILD_DATE,
        "status": "optimized_v2"  # Еще одно изменение для теста кеша
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "build_id": BUILD_ID,
        "build_date": BUILD_DATE,
        "build_marker": BUILD_MARKER
    }
