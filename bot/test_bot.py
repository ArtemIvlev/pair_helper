#!/usr/bin/env python3
"""
Тестовый скрипт для проверки бота
"""

import os
import asyncio
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

async def test_bot():
    """Тестирует подключение к боту"""
    from aiogram import Bot
    
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    print(f"Токен: {token}")
    
    if not token:
        print("❌ Токен не найден!")
        return
    
    try:
        bot = Bot(token=token)
        
        # Получаем информацию о боте
        bot_info = await bot.get_me()
        print(f"✅ Бот подключен: @{bot_info.username}")
        print(f"📝 Имя: {bot_info.first_name}")
        print(f"🆔 ID: {bot_info.id}")
        
        await bot.session.close()
        
    except Exception as e:
        print(f"❌ Ошибка подключения к боту: {e}")

if __name__ == "__main__":
    asyncio.run(test_bot())
