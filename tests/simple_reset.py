#!/usr/bin/env python3
"""
Простой скрипт для очистки данных через прямое подключение к PostgreSQL
"""

import psycopg2
from dotenv import load_dotenv
import os

# Загружаем переменные окружения
load_dotenv()

# Конфигурация базы данных
DB_CONFIG = {
    'host': os.getenv('DB_HOST', '192.168.2.228'),
    'port': int(os.getenv('DB_PORT', '5432')),
    'database': os.getenv('DB_NAME', 'pair_helper'),
    'user': os.getenv('DB_USER', 'admin'),
    'password': os.getenv('DB_PASSWORD', 'Passw0rd')
}

def check_data():
    """Проверяет данные в базе"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("🔍 Проверка данных в базе...")
        print("=" * 50)
        
        # Проверяем пользователей
        cursor.execute("SELECT COUNT(*) FROM users;")
        users_count = cursor.fetchone()[0]
        print(f"👥 Пользователей: {users_count}")
        
        # Проверяем пары
        cursor.execute("SELECT COUNT(*) FROM pairs;")
        pairs_count = cursor.fetchone()[0]
        print(f"💕 Пар: {pairs_count}")
        
        # Проверяем приглашения
        cursor.execute("SELECT COUNT(*) FROM invitations;")
        invitations_count = cursor.fetchone()[0]
        print(f"🎫 Приглашений: {invitations_count}")
        
        # Показываем детали
        if users_count > 0:
            cursor.execute("SELECT id, first_name, telegram_id FROM users;")
            users = cursor.fetchall()
            print("\n👥 Список пользователей:")
            for user in users:
                print(f"  ID: {user[0]}, Имя: {user[1]}, Telegram ID: {user[2]}")
        
        if pairs_count > 0:
            cursor.execute("SELECT id, user1_id, user2_id FROM pairs;")
            pairs = cursor.fetchall()
            print("\n💕 Список пар:")
            for pair in pairs:
                print(f"  ID: {pair[0]}, User1: {pair[1]}, User2: {pair[2]}")
        
        if invitations_count > 0:
            cursor.execute("SELECT id, code, inviter_id, is_used FROM invitations;")
            invitations = cursor.fetchall()
            print("\n🎫 Список приглашений:")
            for inv in invitations:
                print(f"  ID: {inv[0]}, Код: {inv[1]}, Приглашающий: {inv[2]}, Использовано: {inv[3]}")
        
        cursor.close()
        conn.close()
        
        return users_count, pairs_count, invitations_count
        
    except Exception as e:
        print(f"❌ Ошибка подключения к базе данных: {e}")
        return 0, 0, 0

def reset_data():
    """Очищает все данные"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("\n🗑️  Очистка данных...")
        print("=" * 50)
        
        # Отключаем проверку внешних ключей
        cursor.execute("SET session_replication_role = replica;")
        
        # Транкейтим все таблицы public, кроме служебных, с каскадом и сбросом ID
        cursor.execute(r"""
DO $$
DECLARE r record;
BEGIN
  FOR r IN 
    SELECT tablename 
    FROM pg_tables 
    WHERE schemaname = 'public' 
      AND tablename NOT IN ('alembic_version')
  LOOP
    EXECUTE 'TRUNCATE TABLE ' || quote_ident(r.tablename) || ' RESTART IDENTITY CASCADE';
  END LOOP;
END
$$;
""")
        print("✅ Все таблицы очищены (TRUNCATE ... RESTART IDENTITY CASCADE)")
        
        # Включаем проверку внешних ключей
        cursor.execute("SET session_replication_role = DEFAULT;")
        
        # Сохраняем изменения
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\n✅ Очистка завершена!")
        
    except Exception as e:
        print(f"❌ Ошибка очистки данных: {e}")

if __name__ == "__main__":
    print("🗑️  Простой скрипт очистки данных Pair Helper")
    print("=" * 60)
    
    # Проверяем текущие данные
    users, pairs, invitations = check_data()
    
    if users == 0 and pairs == 0 and invitations == 0:
        print("\n✅ База данных уже пустая!")
    else:
        print(f"\n📊 Найдено данных: {users} пользователей, {pairs} пар, {invitations} приглашений")
        
        confirm = input("\n🤔 Очистить все данные? (yes/no): ")
        
        if confirm.lower() in ['yes', 'y', 'да', 'д']:
            reset_data()
            
            print("\n🔍 Проверяем результат...")
            check_data()
        else:
            print("❌ Операция отменена")
