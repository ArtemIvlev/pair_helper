import hashlib
import hmac
import json
import time
from typing import Optional
from urllib.parse import parse_qsl
import logging
from fastapi import HTTPException, status, Depends, Header, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings
from app.models import User


logger = logging.getLogger(__name__)


def verify_telegram_webapp_data(init_data: str) -> dict:
    """Проверяет подпись данных от Telegram Web App"""
    try:
        # Разбираем init_data (URL-decoded пары key=value)
        pairs = dict(parse_qsl(init_data, keep_blank_values=True))
        data_dict = dict(pairs)
        
        # Проверяем время подписи (не старше 60 минут)
        auth_date = data_dict.get('auth_date')
        if auth_date:
            try:
                auth_timestamp = int(auth_date)
                if time.time() - auth_timestamp > 3600:  # 60 минут
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Данные аутентификации устарели"
                    )
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Неверный формат времени аутентификации"
                )
        
        # Убираем hash из данных для проверки
        data_check_string = '\n'.join(
            f"{k}={pairs[k]}" for k in sorted(pairs.keys()) if k != 'hash'
        )
        
        # Получаем секретный ключ бота
        bot_token = settings.TELEGRAM_BOT_TOKEN
        if not bot_token:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Bot token не настроен"
            )
        
        # Вычисляем секретный ключ
        secret_key = hmac.new(
            "WebAppData".encode(),
            bot_token.encode(),
            hashlib.sha256
        ).digest()
        
        # Проверяем подпись
        data_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()
        # Безопасное сравнение
        if not hmac.compare_digest(data_hash, data_dict.get('hash', '')):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверная подпись данных"
            )
        
        return data_dict
        
    except Exception as e:
        logger.warning(f"Telegram auth verify failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ошибка проверки данных Telegram"
        )


def get_current_user(
    x_telegram_init_data: Optional[str] = Header(None),
    db: Session = Depends(get_db),
    request: Request = None,
) -> User:
    """Получает текущего пользователя из Telegram данных"""
    if not x_telegram_init_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Отсутствуют данные Telegram"
        )
    
    # Проверяем подпись
    telegram_data = verify_telegram_webapp_data(x_telegram_init_data)
    
    # Получаем user_id из данных (user приходит как JSON-строка)
    raw_user = telegram_data.get('user')
    user_obj = {}
    if isinstance(raw_user, str):
        try:
            user_obj = json.loads(raw_user)
        except Exception:
            user_obj = {}
    elif isinstance(raw_user, dict):
        user_obj = raw_user

    user_id = None
    if isinstance(user_obj, dict):
        user_id = user_obj.get('id')
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не удалось получить ID пользователя"
        )
    
    # Находим или создаём пользователя
    user = db.query(User).filter(User.telegram_id == user_id).first()
    if not user:
        # Создаём нового пользователя
        user_data = user_obj if isinstance(user_obj, dict) else {}
        user = User(
            telegram_id=user_id,
            first_name=user_data.get('first_name', ''),
            last_name=user_data.get('last_name'),
            username=user_data.get('username')
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # Прокидываем telegram_id в request.state для аналитики
    try:
        if request is not None:
            request.state.telegram_id = user.telegram_id
    except Exception:
        # Не критично, если state недоступен
        pass

    return user
