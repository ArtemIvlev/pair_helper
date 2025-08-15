import logging
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger(__name__)


class InternalAPIMiddleware(BaseHTTPMiddleware):
    """
    Middleware для защиты внутренних API от внешнего доступа.
    Разрешает доступ только с локальных адресов и внутренних сетей.
    """
    
    def __init__(self, app, allowed_networks=None):
        super().__init__(app)
        self.allowed_networks = allowed_networks or [
            "127.0.0.1",      # localhost
            "::1",            # localhost IPv6
            "192.168.",       # локальные сети
            "10.",            # внутренние сети
            "172.16.",        # Docker networks
            "172.17.",        # Docker bridge
            "172.18.",        # Docker compose
        ]
    
    async def dispatch(self, request: Request, call_next):
        # Проверяем, является ли это внутренним API
        if request.url.path.startswith("/api/v1/internal"):
            client_ip = self._get_client_ip(request)
            
            if not self._is_ip_allowed(client_ip):
                logger.warning(f"Попытка доступа к внутреннему API с неразрешенного IP: {client_ip}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Доступ к внутреннему API запрещен"
                )
            
            logger.info(f"Доступ к внутреннему API с IP: {client_ip}")
        
        return await call_next(request)
    
    def _get_client_ip(self, request: Request) -> str:
        """Получает реальный IP клиента с учетом прокси"""
        # Проверяем заголовки прокси
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Берем первый IP из списка
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Если нет заголовков прокси, используем прямой IP
        if request.client:
            return request.client.host
        
        return "unknown"
    
    def _is_ip_allowed(self, ip: str) -> bool:
        """Проверяет, разрешен ли IP для доступа к внутреннему API"""
        if ip == "unknown":
            return False
        
        # Проверяем каждую разрешенную сеть
        for network in self.allowed_networks:
            if ip.startswith(network):
                return True
        
        return False
