#!/usr/bin/env python3
"""
Скрипт для очистки данных в базе данных Pair Helper
Удаляет только пользовательские данные (пользователи, их пары и все связанные записи),
НЕ трогая справочники (вопросы и др.). Можно исключить некоторых пользователей по Telegram ID.

Переменные окружения (опционально):
  - EXCLUDE_TG_IDS: comma-separated список Telegram ID, которых НЕ удалять (например: "123,456")
"""

import requests
import urllib3
from dotenv import load_dotenv
import os

# Загружаем переменные окружения из .env файла
load_dotenv()

# Отключаем предупреждения о SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Конфигурация
PORTAINER_URL = "https://192.168.2.228:31015"
API_BASE_URL = "https://gallery.homoludens.photos/pulse_of_pair/api/v1"

def get_portainer_token():
    """Получает токен аутентификации Portainer"""
    username = os.getenv("PORTAINER_USERNAME", "admin")
    password = os.getenv("PORTAINER_PASSWORD", "admin")
    
    print(f"🔑 Используемые учетные данные: {username}/***")
    print(f"🔗 URL: {PORTAINER_URL}")
    
    try:
        response = requests.post(
            f"{PORTAINER_URL}/api/auth",
            json={"username": username, "password": password},
            verify=False,
            timeout=10
        )
        
        if response.status_code == 200:
            token = response.json().get("jwt")
            print("✅ Токен получен успешно")
            return token
        else:
            print(f"❌ Ошибка получения токена: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Ошибка подключения к Portainer: {e}")
        return None

def get_endpoint_id(token):
    """Получает ID endpoint'а"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{PORTAINER_URL}/api/endpoints",
            headers=headers,
            verify=False,
            timeout=10
        )
        
        if response.status_code == 200:
            endpoints = response.json()
            for endpoint in endpoints:
                if endpoint.get("Name") == "local":
                    print("✅ Endpoint найден: local")
                    return endpoint.get("Id")
            
            print("❌ Endpoint 'local' не найден")
            return None
        else:
            print(f"❌ Ошибка получения endpoints: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Ошибка получения endpoint ID: {e}")
        return None

def execute_sql_command(token, endpoint_id, sql_command):
    """Выполняет SQL команду в контейнере базы данных"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Находим контейнер PostgreSQL
        response = requests.get(
            f"{PORTAINER_URL}/api/endpoints/{endpoint_id}/docker/containers/json",
            headers=headers,
            verify=False,
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"❌ Ошибка получения списка контейнеров: {response.status_code}")
            return False
        
        containers = response.json()
        postgres_container = None
        
        for container in containers:
            names = container.get("Names", [])
            if any("postgres" in name.lower() for name in names):
                postgres_container = container
                break
        
        if not postgres_container:
            print("❌ Контейнер PostgreSQL не найден")
            return False
        
        container_id = postgres_container.get("Id")
        print(f"✅ Контейнер PostgreSQL найден: {container_id[:12]}...")
        
        # Выполняем SQL команду
        exec_data = {
            "AttachStdin": False,
            "AttachStdout": True,
            "AttachStderr": True,
            "Tty": False,
            "Cmd": [
                "psql", "-U", "pair_user", "-d", "pair_helper", "-c", sql_command
            ]
        }
        
        response = requests.post(
            f"{PORTAINER_URL}/api/endpoints/{endpoint_id}/docker/containers/{container_id}/exec",
            headers=headers,
            json=exec_data,
            verify=False,
            timeout=30
        )
        
        if response.status_code == 201:
            exec_id = response.json().get("Id")
            
            # Получаем результат выполнения
            response = requests.post(
                f"{PORTAINER_URL}/api/endpoints/{endpoint_id}/docker/exec/{exec_id}/start",
                headers=headers,
                json={"Detach": False, "Tty": False},
                verify=False,
                timeout=30
            )
            
            if response.status_code == 200:
                print("✅ SQL команда выполнена успешно")
                return True
            else:
                print(f"❌ Ошибка выполнения SQL: {response.status_code}")
                return False
        else:
            print(f"❌ Ошибка создания exec: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка выполнения SQL команды: {e}")
        return False

def reset_database():
    """Очищает только пользовательские данные в базе данных"""
    print("🧹 Очистка пользовательских данных Pair Helper...")
    print("=" * 60)
    
    # Исключения по Telegram ID
    exclude_raw = os.getenv("EXCLUDE_TG_IDS", "").strip()
    exclude_list = [x.strip() for x in exclude_raw.split(",") if x.strip()]
    print(f"🚫 Исключаем Telegram ID: {', '.join(exclude_list) if exclude_list else '—'}")
    exclude_sql = ",".join([f"'{x}'" for x in exclude_list]) or "''"
    
    # Получаем токен
    token = get_portainer_token()
    if not token:
        return False
    
    # Получаем endpoint ID
    endpoint_id = get_endpoint_id(token)
    if not endpoint_id:
        return False
    
    # Таргетированная очистка: удаляем только данные пользователей и их пар
    sql_commands = [f"""
BEGIN;

-- Пользователи к удалению (по telegram_id, исключая явно указанных)
CREATE TEMP TABLE tmp_victim_users AS
  SELECT id FROM users
  WHERE COALESCE(telegram_id::text, '') NOT IN ({exclude_sql});

-- Пары, связанные с этими пользователями
CREATE TEMP TABLE tmp_victim_pairs AS
  SELECT id FROM pairs
  WHERE user1_id IN (SELECT id FROM tmp_victim_users)
     OR user2_id IN (SELECT id FROM tmp_victim_users);

-- Удаляем данные, зависящие от пользователя
DO $$
BEGIN
  BEGIN
    EXECUTE 'DELETE FROM user_answers WHERE user_id IN (SELECT id FROM tmp_victim_users)';
  EXCEPTION WHEN undefined_table THEN NULL; END;

  BEGIN
    EXECUTE 'DELETE FROM user_question_status WHERE user_id IN (SELECT id FROM tmp_victim_users)';
  EXCEPTION WHEN undefined_table THEN NULL; END;

  BEGIN
    EXECUTE 'DELETE FROM mood_entries WHERE user_id IN (SELECT id FROM tmp_victim_users)';
  EXCEPTION WHEN undefined_table THEN NULL; END;

  BEGIN
    EXECUTE 'DELETE FROM appreciations WHERE user_id IN (SELECT id FROM tmp_victim_users)';
  EXCEPTION WHEN undefined_table THEN NULL; END;

  BEGIN
    EXECUTE 'DELETE FROM ritual_checks WHERE user_id IN (SELECT id FROM tmp_victim_users)';
  EXCEPTION WHEN undefined_table THEN NULL; END;

  BEGIN
    EXECUTE 'DELETE FROM calendar_events WHERE user_id IN (SELECT id FROM tmp_victim_users)';
  EXCEPTION WHEN undefined_table THEN NULL; END;

  BEGIN
    EXECUTE 'DELETE FROM female_cycle_logs WHERE user_id IN (SELECT id FROM tmp_victim_users)';
  EXCEPTION WHEN undefined_table THEN NULL; END;

  BEGIN
    EXECUTE 'DELETE FROM female_cycle WHERE user_id IN (SELECT id FROM tmp_victim_users)';
  EXCEPTION WHEN undefined_table THEN NULL; END;

  BEGIN
    EXECUTE 'DELETE FROM emotion_notes WHERE user_id IN (SELECT id FROM tmp_victim_users)';
  EXCEPTION WHEN undefined_table THEN NULL; END;

  BEGIN
    EXECUTE 'DELETE FROM invitations WHERE inviter_id IN (SELECT id FROM tmp_victim_users)';
  EXCEPTION WHEN undefined_table THEN NULL; END;
END$$;

-- Удаляем данные, зависящие от пары
DO $$
BEGIN
  BEGIN
    EXECUTE 'DELETE FROM pair_daily_questions WHERE pair_id IN (SELECT id FROM tmp_victim_pairs)';
  EXCEPTION WHEN undefined_table THEN NULL; END;

  BEGIN
    EXECUTE 'DELETE FROM rituals WHERE pair_id IN (SELECT id FROM tmp_victim_pairs)';
  EXCEPTION WHEN undefined_table THEN NULL; END;
END$$;

-- Удаляем пары
DELETE FROM pairs WHERE id IN (SELECT id FROM tmp_victim_pairs);

-- И только после этого удаляем пользователей
DELETE FROM users WHERE id IN (SELECT id FROM tmp_victim_users);

-- Чистим временные таблицы
DROP TABLE IF EXISTS tmp_victim_pairs;
DROP TABLE IF EXISTS tmp_victim_users;

COMMIT;
"""]
    
    print("🧹 Выполняем очистку данных...")
    
    for i, sql in enumerate(sql_commands, 1):
        print(f"  {i:2d}. Выполняем блок очистки...")
        if not execute_sql_command(token, endpoint_id, sql):
            print(f"❌ Ошибка при выполнении команды {i}")
            return False
    
    print("\n✅ Очистка пользовательских данных завершена успешно!")
    print("📊 Справочники и системные таблицы не тронуты")
    
    return True

if __name__ == "__main__":
    print("🗑️  Скрипт очистки пользовательских данных Pair Helper")
    print("=" * 60)
    print("⚠️  ВНИМАНИЕ: Этот скрипт удалит ПОЛЬЗОВАТЕЛЬСКИЕ данные (пользователи, пары, ответы и т.п.)")
    print("   Справочники (например, вопросы) не затрагиваются.")
    print()
    
    confirm = input("🤔 Вы уверены, что хотите продолжить? (yes/no): ")
    
    if confirm.lower() in ['yes', 'y', 'да', 'д']:
        reset_database()
    else:
        print("❌ Операция отменена")

