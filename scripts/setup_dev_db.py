#!/usr/bin/env python3
"""
Скрипт для настройки dev базы данных в основном PostgreSQL сервере
Создает пользователя и базу данных для dev среды
"""

import psycopg2
import sys
from datetime import datetime

# Настройки основного PostgreSQL сервера
MAIN_DB_CONFIG = {
    'host': '192.168.2.228',
    'port': 5432,
    'database': 'postgres',  # Подключаемся к системной базе
    'user': 'admin',         # Используем существующего пользователя
    'password': 'Passw0rd'   # Пароль от основного пользователя
}

def setup_dev_database():
    """Создание dev базы данных и пользователя"""
    
    print("🔧 Настройка dev базы данных...")
    print(f"📅 Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🗄️  Сервер: {MAIN_DB_CONFIG['host']}:{MAIN_DB_CONFIG['port']}")
    
    try:
        # Подключение к основному PostgreSQL
        conn = psycopg2.connect(**MAIN_DB_CONFIG)
        conn.autocommit = True  # Включаем автокоммит для DDL операций
        cursor = conn.cursor()
        
        print("✅ Подключение к основному PostgreSQL установлено")
        
        # Создание пользователя dev
        try:
            cursor.execute("""
                CREATE USER pair_helper_dev WITH PASSWORD 'dev_password_123';
            """)
            print("👤 Создан пользователь pair_helper_dev")
        except psycopg2.errors.DuplicateObject:
            print("👤 Пользователь pair_helper_dev уже существует")
        
        # Создание dev базы данных
        try:
            cursor.execute("""
                CREATE DATABASE pair_helper_dev OWNER pair_helper_dev;
            """)
            print("🗄️  Создана база данных pair_helper_dev")
        except psycopg2.errors.DuplicateDatabase:
            print("🗄️  База данных pair_helper_dev уже существует")
        
        # Предоставление прав пользователю
        cursor.execute("""
            GRANT ALL PRIVILEGES ON DATABASE pair_helper_dev TO pair_helper_dev;
        """)
        print("🔐 Предоставлены права пользователю pair_helper_dev")
        
        cursor.close()
        conn.close()
        
        print("\n✅ Dev база данных успешно настроена!")
        print("💡 Теперь можно запускать dev сервисы")
        
    except Exception as e:
        print(f"❌ Ошибка при настройке dev базы: {e}")
        print("💡 Убедитесь, что:")
        print("   - Основной PostgreSQL сервер доступен")
        print("   - Пароль в MAIN_DB_CONFIG правильный")
        print("   - У пользователя postgres есть права на создание БД")
        sys.exit(1)

def drop_dev_database():
    """Удаление dev базы данных и пользователя"""
    
    print("🗑️  Удаление dev базы данных...")
    
    try:
        conn = psycopg2.connect(**MAIN_DB_CONFIG)
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Завершаем все активные подключения к dev базе
        cursor.execute("""
            SELECT pg_terminate_backend(pid) 
            FROM pg_stat_activity 
            WHERE datname = 'pair_helper_dev' AND pid <> pg_backend_pid();
        """)
        
        # Удаление dev базы данных
        cursor.execute("DROP DATABASE IF EXISTS pair_helper_dev;")
        print("🗄️  Удалена база данных pair_helper_dev")
        
        # Удаление пользователя
        cursor.execute("DROP USER IF EXISTS pair_helper_dev;")
        print("👤 Удален пользователь pair_helper_dev")
        
        cursor.close()
        conn.close()
        
        print("✅ Dev база данных успешно удалена!")
        
    except Exception as e:
        print(f"❌ Ошибка при удалении dev базы: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--drop":
        drop_dev_database()
    else:
        setup_dev_database()
