import hashlib
import hmac
import json
from typing import Optional
from fastapi import HTTPException, status, Depends, Header
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import User


def verify_telegram_webapp_data(init_data: str) -> dict:
    """Проверяет подпись данных от Telegram Web App"""
    try:
        # Разбираем init_data
        data_dict = {}
        for item in init_data.split('&'):
            if '=' in item:
                key, value = item.split('=', 1)
                data_dict[key] = value
        
        # Убираем hash из данных для проверки
        data_check_string = '\n'.join([
            f"{k}={v}" for k, v in sorted(data_dict.items()) 
            if k != 'hash'
        ])
        
        # Получаем секретный ключ бота
        bot_token = "YOUR_BOT_TOKEN"  # TODO: получить из настроек
        
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
        
        if data_hash != data_dict.get('hash'):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверная подпись данных"
            )
        
        return data_dict
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ошибка проверки данных Telegram"
        )


def get_current_user(
    x_telegram_init_data: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """Получает текущего пользователя из Telegram данных"""
    if not x_telegram_init_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Отсутствуют данные Telegram"
        )
    
    # Проверяем подпись
    telegram_data = verify_telegram_webapp_data(x_telegram_init_data)
    
    # Получаем user_id из данных
    user_id = telegram_data.get('user', {}).get('id')
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не удалось получить ID пользователя"
        )
    
    # Находим или создаём пользователя
    user = db.query(User).filter(User.telegram_id == user_id).first()
    if not user:
        # Создаём нового пользователя
        user_data = json.loads(telegram_data.get('user', '{}'))
        user = User(
            telegram_id=user_id,
            first_name=user_data.get('first_name', ''),
            last_name=user_data.get('last_name'),
            username=user_data.get('username')
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    return user
