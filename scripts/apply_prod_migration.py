#!/usr/bin/env python3
"""
Скрипт для применения миграции на продакшне
"""

import os
import sys
import subprocess
from dotenv import load_dotenv

# Загружаем продакшн конфигурацию
load_dotenv('.env')

def apply_migration():
    """Применяет миграцию на продакшн базе данных"""
    
    # Проверяем, что мы в правильной директории
    if not os.path.exists('backend/alembic.ini'):
        print("❌ Ошибка: alembic.ini не найден. Запустите скрипт из корня проекта.")
        return False
    
    # Переходим в директорию backend
    os.chdir('backend')
    
    try:
        print("🔄 Применяем миграцию на продакшн...")
        
        # Применяем миграцию
        result = subprocess.run([
            'alembic', 'upgrade', 'head'
        ], capture_output=True, text=True, check=True)
        
        print("✅ Миграция успешно применена!")
        print(result.stdout)
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при применении миграции: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Применение миграции на продакшн")
    print("=" * 50)
    
    success = apply_migration()
    
    if success:
        print("\n✅ Миграция применена успешно!")
        print("🔄 Теперь квиз 'Сонастройка' должен работать корректно")
    else:
        print("\n❌ Ошибка при применении миграции!")
        sys.exit(1)
