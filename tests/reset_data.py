#!/usr/bin/env python3
"""
Скрипт для очистки данных в базе данных Pair Helper
Удаляет всех пользователей, пары, приглашения и другие данные
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
    """Очищает все данные в базе данных"""
    print("🗑️  Очистка данных Pair Helper...")
    print("=" * 60)
    
    # Получаем токен
    token = get_portainer_token()
    if not token:
        return False
    
    # Получаем endpoint ID
    endpoint_id = get_endpoint_id(token)
    if not endpoint_id:
        return False
    
    # Универсальная очистка: TRUNCATE всех таблиц public (кроме служебных),
    # сброс идентификаторов и каскад для внешних ключей
    sql_commands = [
        r"""
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
"""
    ]
    
    print("🧹 Выполняем очистку данных...")
    
    for i, sql in enumerate(sql_commands, 1):
        print(f"  {i:2d}. Выполняем блок очистки...")
        if not execute_sql_command(token, endpoint_id, sql):
            print(f"❌ Ошибка при выполнении команды {i}")
            return False
    
    print("\n✅ Очистка данных завершена успешно!")
    print("📊 База данных полностью очищена")
    print("🔄 Все последовательности сброшены")
    
    return True

if __name__ == "__main__":
    print("🗑️  Скрипт очистки данных Pair Helper")
    print("=" * 60)
    print("⚠️  ВНИМАНИЕ: Этот скрипт удалит ВСЕ данные!")
    print("   Пользователи, пары, приглашения, записи - всё будет удалено!")
    print()
    
    confirm = input("🤔 Вы уверены, что хотите продолжить? (yes/no): ")
    
    if confirm.lower() in ['yes', 'y', 'да', 'д']:
        reset_database()
    else:
        print("❌ Операция отменена")

