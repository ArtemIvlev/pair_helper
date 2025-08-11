#!/usr/bin/env python3
"""
Скрипт для сброса dev базы данных
Используется только для dev среды!
"""

import os
import psycopg2
import sys
from datetime import datetime

# Dev настройки базы данных (используем основной PostgreSQL сервер)
DEV_DB_CONFIG = {
    'host': '192.168.2.228',
    'port': 5432,
    'database': 'pair_helper_dev',
    'user': 'admin',
    'password': 'Passw0rd'
}

def reset_dev_database():
    """Сброс dev базы данных - удаляет только пользовательские данные"""
    
    print("🔄 Сброс dev базы данных...")
    print(f"📅 Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🗄️  База: {DEV_DB_CONFIG['database']} на {DEV_DB_CONFIG['host']}:{DEV_DB_CONFIG['port']}")
    
    try:
        # Подключение к dev базе
        conn = psycopg2.connect(**DEV_DB_CONFIG)
        cursor = conn.cursor()
        
        print("✅ Подключение к dev базе установлено")
        
        # Список таблиц для очистки (только пользовательские данные)
        tables_to_clear = [
            'user_answers',
            'pair_daily_questions', 
            'pairs',
            'invitations',
            'users'
        ]
        
        # Очистка таблиц
        for table in tables_to_clear:
            try:
                cursor.execute(f"DELETE FROM {table}")
                deleted_count = cursor.rowcount
                print(f"🗑️  Удалено {deleted_count} записей из {table}")
            except Exception as e:
                print(f"⚠️  Ошибка при очистке {table}: {e}")
        
        # Сброс автоинкрементов
        sequences_to_reset = [
            'user_answers_id_seq',
            'pair_daily_questions_id_seq',
            'pairs_id_seq', 
            'invitations_id_seq',
            'users_id_seq'
        ]
        
        for sequence in sequences_to_reset:
            try:
                cursor.execute(f"ALTER SEQUENCE {sequence} RESTART WITH 1")
                print(f"🔄 Сброшен автоинкремент {sequence}")
            except Exception as e:
                print(f"⚠️  Ошибка при сбросе {sequence}: {e}")
        
        # Коммит изменений
        conn.commit()
        print("✅ Изменения сохранены в базе")
        
        # Проверяем, что таблицы пустые
        print("\n📊 Проверка состояния базы:")
        for table in tables_to_clear:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   {table}: {count} записей")
        
        # Проверяем, что вопросы остались
        cursor.execute("SELECT COUNT(*) FROM questions")
        questions_count = cursor.fetchone()[0]
        print(f"   questions: {questions_count} записей (сохранены)")
        
        cursor.execute("SELECT COUNT(*) FROM admin_users")
        admin_count = cursor.fetchone()[0]
        print(f"   admin_users: {admin_count} записей (сохранены)")
        
        cursor.close()
        conn.close()
        
        print("\n✅ Dev база данных успешно сброшена!")
        print("💡 Пользовательские данные удалены, вопросы и админы сохранены")
        
    except Exception as e:
        print(f"❌ Ошибка при сбросе dev базы: {e}")
        sys.exit(1)

def seed_dev_data():
    """Заполнение dev базы тестовыми данными"""
    
    print("🌱 Заполнение dev базы тестовыми данными...")
    
    try:
        conn = psycopg2.connect(**DEV_DB_CONFIG)
        cursor = conn.cursor()
        
        # Добавляем тестового админа если его нет
        cursor.execute("SELECT COUNT(*) FROM admin_users WHERE username = 'dev_admin'")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO admin_users (username, password_hash, created_at) 
                VALUES ('dev_admin', 'dev_password_hash', NOW())
            """)
            print("👤 Добавлен тестовый админ: dev_admin")
        
        # Добавляем тестовые вопросы если их нет
        cursor.execute("SELECT COUNT(*) FROM questions")
        if cursor.fetchone()[0] == 0:
            test_questions = [
                (1, "Какое твое любимое место для свиданий?", "отношения"),
                (2, "Что тебя больше всего привлекает в партнере?", "отношения"),
                (3, "Какое твое самое яркое воспоминание о нас?", "воспоминания"),
                (4, "Что бы ты хотел изменить в наших отношениях?", "отношения"),
                (5, "Какое твое самое большое достижение в жизни?", "личное")
            ]
            
            for number, text, category in test_questions:
                cursor.execute("""
                    INSERT INTO questions (number, text, category, created_at) 
                    VALUES (%s, %s, %s, NOW())
                """, (number, text, category))
            
            print(f"❓ Добавлено {len(test_questions)} тестовых вопросов")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ Dev база заполнена тестовыми данными")
        
    except Exception as e:
        print(f"❌ Ошибка при заполнении dev базы: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--seed":
        seed_dev_data()
    else:
        reset_dev_database()
