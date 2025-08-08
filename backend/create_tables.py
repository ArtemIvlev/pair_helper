#!/usr/bin/env python3
"""
Скрипт для создания таблиц в базе данных
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

# Загружаем переменные окружения
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from app.core.database import engine
from app.models import Base

def create_tables():
    """Создает все таблицы в базе данных"""
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Таблицы созданы успешно!")
        return True
    except Exception as e:
        print(f"❌ Ошибка при создании таблиц: {e}")
        return False

if __name__ == "__main__":
    create_tables()
