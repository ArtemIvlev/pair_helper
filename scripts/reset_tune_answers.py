#!/usr/bin/env python3
"""
Скрипт для удаления всех ответов квиза "Сонастройка" в dev окружении
"""

import os
import sys
from datetime import datetime
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Загружаем переменные окружения
load_dotenv('.env.dev')

def reset_tune_answers():
    """Удаляет все ответы квиза 'Сонастройка'"""
    
    # Получаем параметры подключения к БД
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("❌ Ошибка: DATABASE_URL не найден в .env.dev")
        return False
    
    try:
        # Создаем подключение к БД
        engine = create_engine(db_url)
        
        with engine.connect() as conn:
            # Проверяем количество ответов перед удалением
            result = conn.execute(text("SELECT COUNT(*) FROM tune_answers"))
            count_before = result.scalar()
            
            print(f"📊 Найдено ответов квиза 'Сонастройка': {count_before}")
            
            if count_before == 0:
                print("ℹ️  Ответов для удаления нет")
                return True
            
            # Удаляем все ответы
            result = conn.execute(text("DELETE FROM tune_answers"))
            deleted_count = result.rowcount
            
            # Подтверждаем изменения
            conn.commit()
            
            print(f"✅ Удалено ответов: {deleted_count}")
            print(f"🕐 Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            return True
            
    except Exception as e:
        print(f"❌ Ошибка при удалении ответов: {e}")
        return False

if __name__ == "__main__":
    print("🧹 Удаление ответов квиза 'Сонастройка' в dev окружении")
    print("=" * 60)
    
    success = reset_tune_answers()
    
    if success:
        print("\n✅ Операция завершена успешно!")
        print("🔄 Теперь можно заново протестировать квиз 'Сонастройка'")
    else:
        print("\n❌ Операция завершена с ошибкой!")
        sys.exit(1)
