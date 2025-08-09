#!/usr/bin/env python3
"""
Скрипт для просмотра логов админки Pair Helper
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
            json={"username": username, "password": password},
            verify=False,
            timeout=10
        )
        if response.status_code == 200:
            return response.json().get("token")
        else:
            print(f"Ошибка аутентификации: {response.status_code}")
            return None
    except Exception as e:
        print(f"Ошибка при получении токена: {e}")
        return None

def get_container_logs(base_url, token, container_name, lines=50):
    """Получает логи контейнера"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Сначала получаем список контейнеров
        response = requests.get(
            f"{base_url}/api/endpoints/2/docker/containers/json?all=true",
            headers=headers,
            verify=False,
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"Ошибка получения списка контейнеров: {response.status_code}")
            return None
        
        containers = response.json()
        
        # Ищем нужный контейнер
        target_container = None
        for container in containers:
            names = container.get('Names', [])
            for name in names:
                if container_name in name:
                    target_container = container
                    break
            if target_container:
                break
        
        if not target_container:
            print(f"Контейнер с именем '{container_name}' не найден")
            print("Доступные контейнеры:")
            for container in containers:
                names = container.get('Names', [])
                print(f"  - {names}")
            return None
        
        container_id = target_container['Id']
        
        # Получаем логи
        response = requests.get(
            f"{base_url}/api/endpoints/2/docker/containers/{container_id}/logs",
            headers=headers,
            params={
                'stdout': 'true',
                'stderr': 'true',
                'tail': str(lines),
                'timestamps': 'true'
            },
            verify=False,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.text
        else:
            print(f"Ошибка получения логов: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Ошибка при получении логов: {e}")
        return None

def main():
    # Настройки Portainer
    PORTAINER_URL = os.getenv('PORTAINER_URL', 'https://192.168.2.228:31015')
    PORTAINER_USERNAME = os.getenv('PORTAINER_USERNAME', 'admin')
    PORTAINER_PASSWORD = os.getenv('PORTAINER_PASSWORD', 'your_password_here')
    
    print("🔍 Получение логов админки Pair Helper...")
    print(f"Подключение к Portainer: {PORTAINER_URL}")
    
    # Получаем токен
    token = get_auth_token(PORTAINER_URL, PORTAINER_USERNAME, PORTAINER_PASSWORD)
    if not token:
        print("❌ Не удалось получить токен аутентификации")
        return
    
    print("✅ Токен получен успешно")
    
    # Получаем логи админки
    logs = get_container_logs(PORTAINER_URL, token, 'pair-helper-admin', lines=100)
    
    if logs:
        print("📋 Логи админки (последние 100 строк):")
        print("=" * 80)
        
        # Обрабатываем логи (убираем служебные символы Docker)
        lines = logs.split('\n')
        for line in lines:
            if line.strip():
                # Убираем первые 8 байт (Docker header)
                if len(line) > 8:
                    clean_line = line[8:]
                    print(clean_line)
                else:
                    print(line)
    else:
        print("❌ Не удалось получить логи админки")

if __name__ == "__main__":
    main()

