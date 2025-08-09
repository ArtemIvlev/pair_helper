#!/usr/bin/env python3
"""
Скрипт для проверки базы данных
"""

import os
import psycopg2
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

def check_database():
    """Проверяет состояние базы данных"""
    try:
        # Подключаемся к базе данных
        conn = psycopg2.connect(
            host="192.168.2.228",
            database="pair_helper",
            user="admin",
            password="Passw0rd"
        )
        
        cursor = conn.cursor()
        
        # Проверяем таблицы
        print("📊 Структура базы данных:")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        for table in tables:
            print(f"  - {table[0]}")
        
        print(f"\n📋 Всего таблиц: {len(tables)}")
        
        # Проверяем количество вопросов
        cursor.execute("SELECT COUNT(*) FROM daily_questions;")
        questions_count = cursor.fetchone()[0]
        print(f"❓ Вопросов дня: {questions_count}")
        
        # Показываем несколько примеров вопросов
        cursor.execute("SELECT id, text FROM daily_questions LIMIT 3;")
        questions = cursor.fetchall()
        print("\n📝 Примеры вопросов:")
        for q_id, text in questions:
            print(f"  {q_id}. {text}")
        
        # Проверяем пользователей
        cursor.execute("SELECT COUNT(*) FROM users;")
        users_count = cursor.fetchone()[0]
        print(f"\n👥 Пользователей: {users_count}")
        
        # Проверяем пары
        cursor.execute("SELECT COUNT(*) FROM pairs;")
        pairs_count = cursor.fetchone()[0]
        print(f"💕 Пар: {pairs_count}")
        
        cursor.close()
        conn.close()
        
        print("\n✅ База данных работает корректно!")
        
    except Exception as e:
        print(f"❌ Ошибка при проверке базы данных: {e}")

if __name__ == "__main__":
    check_database()
