#!/usr/bin/env python3
"""
Скрипт для просмотра логов бота Pair Helper
"""

import requests
import json
from urllib3.exceptions import InsecureRequestWarning
import urllib3
import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Отключаем предупреждения о SSL
urllib3.disable_warnings(InsecureRequestWarning)

def get_auth_token(base_url, username, password):
    """Получает токен аутентификации"""
    try:
        response = requests.post(
            f"{base_url}/api/auth",
            json={"Username": username, "Password": password},
            verify=False,
            timeout=10
        )
        if response.status_code == 200:
            return response.json().get("jwt")
        else:
            print(f"❌ Ошибка аутентификации: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Ошибка при получении токена: {e}")
        return None

def get_endpoints(base_url, token):
    """Получает список endpoints"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{base_url}/api/endpoints",
            headers=headers,
            verify=False,
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Ошибка получения endpoints: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Ошибка при получении endpoints: {e}")
        return []

def get_containers(base_url, token, endpoint_id):
    """Получает список контейнеров"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{base_url}/api/endpoints/{endpoint_id}/docker/containers/json",
            headers=headers,
            verify=False,
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Ошибка получения контейнеров: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Ошибка при получении контейнеров: {e}")
        return []

def get_container_logs(base_url, token, endpoint_id, container_id, lines=100):
    """Получает логи контейнера"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{base_url}/api/endpoints/{endpoint_id}/docker/containers/{container_id}/logs",
            params={"stdout": True, "stderr": True, "tail": lines},
            headers=headers,
            verify=False,
            timeout=30
        )
        if response.status_code == 200:
            return response.text
        else:
            return f"❌ Ошибка получения логов: {response.status_code}"
    except Exception as e:
        return f"❌ Ошибка при получении логов: {e}"

def main():
    print("🤖 Детальный просмотр логов бота Pair Helper...")
    print("=" * 60)
    
    # Конфигурация
    base_url = "https://192.168.2.228:31015"
    username = os.getenv("PORTAINER_USERNAME", "admin")
    password = os.getenv("PORTAINER_PASSWORD", "admin")
    
    print(f"🔑 Используемые учетные данные: {username}/***")
    print(f"🔗 URL: {base_url}")
    print()
    
    # Получаем токен
    print("1. Получение токена аутентификации...")
    token = get_auth_token(base_url, username, password)
    if not token:
        print("❌ Не удалось получить токен аутентификации")
        return
    
    print("✅ Токен получен успешно")
    print()
    
    # Получаем endpoints
    print("2. Получение списка endpoints...")
    endpoints = get_endpoints(base_url, token)
    if not endpoints:
        print("❌ Не удалось получить endpoints")
        return
    
    # Ищем нужный endpoint (обычно первый)
    endpoint = endpoints[0] if endpoints else None
    if not endpoint:
        print("❌ Endpoint не найден")
        return
    
    endpoint_id = endpoint.get("Id")
    print(f"✅ Endpoint найден: {endpoint.get('Name', 'Unknown')} (ID: {endpoint_id})")
    print()
    
    # Получаем контейнеры
    print("3. Поиск контейнера бота...")
    containers = get_containers(base_url, token, endpoint_id)
    if not containers:
        print("❌ Не удалось получить контейнеры")
        return
    
    # Ищем контейнер бота
    bot_container = None
    for container in containers:
        names = container.get("Names", [])
        if any("pair-helper-bot" in name for name in names):
            bot_container = container
            break
    
    if not bot_container:
        print("❌ Контейнер pair-helper-bot не найден")
        return
    
    container_id = bot_container["Id"]
    container_name = bot_container["Names"][0] if bot_container["Names"] else "Unknown"
    container_status = bot_container.get("State", "Unknown")
    
    print(f"✅ Контейнер найден: {container_name}")
    print(f"   ID: {container_id[:12]}...")
    print(f"   Состояние: {container_status}")
    print()
    
    # Получаем логи
    print("4. Получение логов бота...")
    print("-" * 60)
    logs = get_container_logs(base_url, token, endpoint_id, container_id, lines=300)
    print(logs)
    print("-" * 60)
    
    print("✅ Просмотр логов завершен!")

if __name__ == "__main__":
    main()

