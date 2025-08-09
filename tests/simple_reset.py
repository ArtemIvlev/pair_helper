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
    """Очищает только пользовательские данные, оставляя справочники"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("\n🗑️  Очистка пользовательских данных...")
        print("=" * 50)
        
        # Получаем исключения из переменной окружения
        exclude_tg_ids_str = os.getenv("EXCLUDE_TG_IDS", "")
        exclude_tg_ids = [int(x.strip()) for x in exclude_tg_ids_str.split(',') if x.strip()]
        
        if exclude_tg_ids:
            print(f"🚫 Исключаем Telegram ID: {', '.join(map(str, exclude_tg_ids))}")
            exclude_condition = f"WHERE telegram_id NOT IN ({','.join(map(str, exclude_tg_ids))})"
            user_filter = f"WHERE user_id IN (SELECT id FROM users {exclude_condition})"
            pair_filter = f"WHERE pair_id IN (SELECT id FROM pairs WHERE user1_id IN (SELECT id FROM users {exclude_condition}) OR user2_id IN (SELECT id FROM users {exclude_condition}))"
        else:
            print("🚫 Исключаем Telegram ID: —")
            user_filter = ""
            pair_filter = ""
            exclude_condition = ""
        
        # SQL команды для очистки пользовательских данных в правильном порядке
        sql_commands = [
            f"DELETE FROM emotion_notes {user_filter};",
            f"DELETE FROM calendar_events {user_filter};",
            f"DELETE FROM rituals {pair_filter};",
            f"DELETE FROM user_answers {user_filter};",
            f"DELETE FROM user_question_status {user_filter};",
            f"DELETE FROM pair_daily_questions {pair_filter};",
            f"DELETE FROM female_cycle_logs {user_filter};",
            f"DELETE FROM female_cycles {user_filter};",
            f"DELETE FROM pair_invites {user_filter.replace('user_id', 'owner_user_id') if user_filter else ''};",
            f"DELETE FROM invitations {user_filter.replace('user_id', 'inviter_id') if user_filter else ''};",
            f"DELETE FROM pairs WHERE user1_id IN (SELECT id FROM users {exclude_condition}) OR user2_id IN (SELECT id FROM users {exclude_condition});" if exclude_condition else "DELETE FROM pairs;",
            f"DELETE FROM users {exclude_condition};"
        ]
        
        print("🧹 Удаляем пользовательские данные...")
        for i, sql in enumerate(sql_commands, 1):
            try:
                cursor.execute(sql)
                print(f"  ✅ {i:2d}. Выполнено")
            except Exception as e:
                print(f"  ❌ {i:2d}. Ошибка: {e}")
                raise
        
        # Сброс последовательностей для очищенных таблиц
        sequences = [
            "users_id_seq", "pairs_id_seq", "pair_invites_id_seq",
            "user_answers_id_seq", "user_question_status_id_seq", 
            "pair_daily_questions_id_seq", "emotion_notes_id_seq",
            "calendar_events_id_seq", "rituals_id_seq",
            "female_cycles_id_seq", "female_cycle_logs_id_seq",
            "invitations_id_seq"
        ]
        
        print("\n🔄 Сбрасываем последовательности...")
        for seq in sequences:
            try:
                cursor.execute(f"ALTER SEQUENCE {seq} RESTART WITH 1;")
            except Exception:
                # Последовательность может не существовать - игнорируем
                pass
        
        # Сохраняем изменения
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\n✅ Очистка пользовательских данных завершена!")
        print("📊 Справочники (вопросы, админы) сохранены")
        
    except Exception as e:
        print(f"❌ Ошибка очистки данных: {e}")

if __name__ == "__main__":
    print("🗑️  Простой скрипт очистки пользовательских данных Pair Helper")
    print("=" * 60)
    print("⚠️  ВНИМАНИЕ: Этот скрипт удалит ПОЛЬЗОВАТЕЛЬСКИЕ данные (пользователи, пары, ответы и т.п.)")
    print("   Справочники (например, вопросы) не затрагиваются.")
    print()
    
    # Проверяем текущие данные
    users, pairs, invitations = check_data()
    
    if users == 0 and pairs == 0 and invitations == 0:
        print("\n✅ База данных уже пустая!")
    else:
        print(f"\n📊 Найдено данных: {users} пользователей, {pairs} пар, {invitations} приглашений")
        
        confirm = input("\n🤔 Очистить пользовательские данные? (yes/no): ")
        
        if confirm.lower() in ['yes', 'y', 'да', 'д']:
            reset_data()
            
            print("\n🔍 Проверяем результат...")
            check_data()
        else:
            print("❌ Операция отменена")
