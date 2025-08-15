#!/usr/bin/env python3
"""
Тест для проверки работы TelegramIdMiddleware
"""

import asyncio
import json
from urllib.parse import parse_qsl

def extract_telegram_id_from_data(init_data: str):
    """Извлекает telegram_id из данных Telegram без полной валидации"""
    try:
        # Разбираем init_data (URL-decoded пары key=value)
        pairs = dict(parse_qsl(init_data, keep_blank_values=True))
        data_dict = dict(pairs)
        
        # Получаем user_id из данных (user приходит как JSON-строка)
        raw_user = data_dict.get('user')
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
        
        return user_id
    except Exception as e:
        print(f"Error extracting telegram_id: {e}")
        return None

def test_extract_telegram_id():
    """Тестируем извлечение telegram_id"""
    test_data = "user=%7B%22id%22%3A123456%7D&auth_date=1755204786&hash=test"
    
    print("🧪 Тестируем извлечение telegram_id...")
    print(f"📝 Тестовые данные: {test_data}")
    
    telegram_id = extract_telegram_id_from_data(test_data)
    print(f"✅ Результат: telegram_id = {telegram_id}")
    
    if telegram_id == 123456:
        print("🎉 Тест прошел успешно!")
        return True
    else:
        print("❌ Тест не прошел!")
        return False

if __name__ == "__main__":
    test_extract_telegram_id()
