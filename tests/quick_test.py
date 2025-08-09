#!/usr/bin/env python3
"""
Быстрая проверка API эндпоинтов
"""

import requests
import json
from urllib3.exceptions import InsecureRequestWarning
import urllib3

# Отключаем предупреждения о SSL
urllib3.disable_warnings(InsecureRequestWarning)

def test_api():
    base_url = "http://192.168.2.228:8000/api"
    
    print("🔍 Тестирование API эндпоинтов...")
    print(f"Base URL: {base_url}")
    print("=" * 50)
    
    # Тест 1: Документация API
    print("1. Проверка документации API...")
    try:
        response = requests.get(f"{base_url}/docs", verify=False, timeout=10)
        print(f"   Статус: {response.status_code}")
        print(f"   Успех: {response.status_code == 200}")
    except Exception as e:
        print(f"   Ошибка: {e}")
    
    # Тест 2: Эндпоинт пользователей
    print("\n2. Проверка эндпоинта пользователей...")
    try:
        response = requests.get(f"{base_url}/v1/users/me?telegram_id=123", verify=False, timeout=10)
        print(f"   Статус: {response.status_code}")
        print(f"   Успех: {response.status_code in [200, 404]}")  # 404 тоже нормально для несуществующего пользователя
    except Exception as e:
        print(f"   Ошибка: {e}")
    
    # Тест 3: Эндпоинт приглашений (должен быть 404 для несуществующего пользователя)
    print("\n3. Проверка эндпоинта приглашений...")
    try:
        response = requests.post(f"{base_url}/v1/invitations/generate?inviter_telegram_id=999999", verify=False, timeout=10)
        print(f"   Статус: {response.status_code}")
        print(f"   Успех: {response.status_code in [200, 404]}")  # 404 нормально для несуществующего пользователя
        if response.status_code != 404:
            print(f"   Ответ: {response.text[:200]}")
    except Exception as e:
        print(f"   Ошибка: {e}")
    
    # Тест 4: Проверка доступности эндпоинта приглашений
    print("\n4. Проверка доступности эндпоинта приглашений...")
    try:
        response = requests.get(f"{base_url}/v1/invitations/test", verify=False, timeout=10)
        print(f"   Статус: {response.status_code}")
        print(f"   Доступен: {response.status_code != 404}")  # Любой ответ кроме 404 означает что роутер работает
    except Exception as e:
        print(f"   Ошибка: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Тестирование завершено!")

if __name__ == "__main__":
    test_api()
