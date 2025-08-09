#!/usr/bin/env python3
"""
Упрощенная проверка логов контейнеров
"""

import requests
import json
from urllib3.exceptions import InsecureRequestWarning
import urllib3
from dotenv import load_dotenv
import os

# Загружаем переменные окружения из .env файла
load_dotenv()

# Отключаем предупреждения о SSL
urllib3.disable_warnings(InsecureRequestWarning)

def check_portainer_access():
    base_url = "https://192.168.2.228:31015"
    
    # Получаем учетные данные из переменных окружения
    username = os.getenv("PORTAINER_USERNAME", "admin")
    password = os.getenv("PORTAINER_PASSWORD", "admin")
    
    print(f"🔑 Используемые учетные данные: {username}/{password}")
    print(f"💡 Если это неправильно, установите переменные окружения:")
    print(f"   export PORTAINER_USERNAME=your_username")
    print(f"   export PORTAINER_PASSWORD=your_password")
    print()
    
    print("🔍 Проверка доступа к Portainer...")
    print(f"URL: {base_url}")
    print("=" * 50)
    
    # Тест 1: Проверка доступности Portainer
    print("1. Проверка доступности Portainer...")
    try:
        response = requests.get(f"{base_url}/api/status", verify=False, timeout=10)
        print(f"   Статус: {response.status_code}")
        print(f"   Ответ: {response.text[:200]}")
    except Exception as e:
        print(f"   Ошибка: {e}")
    
    # Тест 2: Попытка аутентификации с разными данными
    print("\n2. Тест аутентификации...")
    
    test_credentials = [
        {"username": username, "password": password},
        {"username": "admin", "password": "admin"},
        {"username": "admin", "password": "password"},
        {"username": "admin", "password": "123456"},
        {"username": "root", "password": "admin"}
    ]
    
    for creds in test_credentials:
        try:
            auth_url = f"{base_url}/api/auth"
            auth_data = {
                "Username": creds["username"],
                "Password": creds["password"]
            }
            
            response = requests.post(auth_url, json=auth_data, verify=False, timeout=10)
            print(f"   {creds['username']}/{creds['password']}: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ Успешная аутентификация!")
                token = response.json().get("jwt")
                print(f"   Токен: {token[:50]}..." if token else "   Токен не получен")
                break
            elif response.status_code == 422:
                print(f"   ❌ Неверный формат данных")
            elif response.status_code == 401:
                print(f"   ❌ Неверные учетные данные")
            else:
                print(f"   ❓ Неизвестная ошибка: {response.text[:100]}")
                
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Проверка завершена!")

if __name__ == "__main__":
    check_portainer_access()
