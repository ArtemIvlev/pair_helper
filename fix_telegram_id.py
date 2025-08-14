#!/usr/bin/env python3
import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Подключение к базе данных
DATABASE_URL = "postgresql://admin:Passw0rd@192.168.2.228:5432/pair_helper"

def fix_telegram_id_type():
    try:
        # Подключаемся к базе данных
        conn = psycopg2.connect(DATABASE_URL)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print("Подключение к базе данных установлено")
        
        # Проверяем текущий тип данных
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'invitations' AND column_name = 'invitee_telegram_id'
        """)
        
        result = cursor.fetchone()
        if result:
            print(f"Текущий тип данных: {result[1]}")
        
        # Изменяем тип данных
        print("Изменяем тип данных с INTEGER на BIGINT...")
        cursor.execute("ALTER TABLE invitations ALTER COLUMN invitee_telegram_id TYPE BIGINT")
        
        # Проверяем результат
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'invitations' AND column_name = 'invitee_telegram_id'
        """)
        
        result = cursor.fetchone()
        if result:
            print(f"Новый тип данных: {result[1]}")
            print("✅ Тип данных успешно изменен!")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    fix_telegram_id_type()
