import time
from typing import Dict, Optional
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import logging

logger = logging.getLogger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware для ограничения количества запросов"""
    
    def __init__(self, app, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.calls = calls  # Максимум запросов
        self.period = period  # Период в секундах
        self.clients: Dict[str, Dict] = {}
    
    async def dispatch(self, request: Request, call_next):
        # Получаем IP клиента
        client_ip = request.client.host
        current_time = time.time()
        
        # Очищаем старые записи
        self.cleanup_old_entries(current_time)
        
        # Проверяем лимит для клиента
        if client_ip not in self.clients:
            self.clients[client_ip] = {
                'requests': [],
                'blocked_until': 0
            }
        
        client_data = self.clients[client_ip]
        
        # Проверяем, не заблокирован ли клиент
        if current_time < client_data['blocked_until']:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Слишком много запросов. Попробуйте позже."
            )
        
        # Фильтруем запросы за последний период
        recent_requests = [
            req_time for req_time in client_data['requests']
            if current_time - req_time < self.period
        ]
        
        # Проверяем лимит
        if len(recent_requests) >= self.calls:
            # Блокируем клиента на период
            client_data['blocked_until'] = current_time + self.period
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Превышен лимит запросов ({self.calls} за {self.period} сек)"
            )
        
        # Добавляем текущий запрос
        recent_requests.append(current_time)
        client_data['requests'] = recent_requests
        
        response = await call_next(request)
        return response
    
    def cleanup_old_entries(self, current_time: float):
        """Удаляем старые записи для экономии памяти"""
        for client_ip in list(self.clients.keys()):
            client_data = self.clients[client_ip]
            
            # Удаляем старые запросы
            client_data['requests'] = [
                req_time for req_time in client_data['requests']
                if current_time - req_time < self.period * 2
            ]
            
            # Удаляем клиента если нет активности
            if (not client_data['requests'] and 
                current_time > client_data['blocked_until']):
                del self.clients[client_ip]


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware для добавления заголовков безопасности"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Добавляем заголовки безопасности
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        # HSTS только если запрос пришел через HTTPS (проверяем заголовок от nginx)
        if request.headers.get("x-forwarded-proto") == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://telegram.org; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https://api.telegram.org"
        )
        
        return response


class ProxyHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware для обработки заголовков от nginx прокси"""
    
    async def dispatch(self, request: Request, call_next):
        # Получаем реальный IP из заголовков nginx
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            # Берем первый IP (реальный клиент)
            real_ip = forwarded_for.split(",")[0].strip()
            # Обновляем информацию о клиенте
            request.scope["client"] = (real_ip, 0)
        
        # Обрабатываем протокол
        forwarded_proto = request.headers.get("x-forwarded-proto")
        if forwarded_proto:
            request.scope["scheme"] = forwarded_proto
        
        response = await call_next(request)
        return response


class TelegramValidationMiddleware(BaseHTTPMiddleware):
    """Middleware для дополнительной валидации Telegram запросов"""
    
    async def dispatch(self, request: Request, call_next):
        # Проверяем только API эндпоинты
        if request.url.path.startswith("/api/"):
            # Проверяем наличие Telegram заголовков
            telegram_data = request.headers.get("X-Telegram-Init-Data")
            if telegram_data:
                # Дополнительные проверки
                if len(telegram_data) > 4096:  # Максимальный размер
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Данные Telegram слишком большие"
                    )
                
                # Проверяем на подозрительные символы
                if any(char in telegram_data for char in ['<', '>', '"', "'"]):
                    logger.warning(f"Suspicious characters in Telegram data from {request.client.host}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Некорректные данные"
                    )
        
        response = await call_next(request)
        return response
