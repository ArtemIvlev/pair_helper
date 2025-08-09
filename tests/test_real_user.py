#!/usr/bin/env python3
"""
Тест с реальным пользователем
"""

import requests
import json
from urllib3.exceptions import InsecureRequestWarning
import urllib3

# Отключаем предупреждения о SSL
urllib3.disable_warnings(InsecureRequestWarning)

def test_with_real_user():
    base_url = "http://192.168.2.228:8000/api"
    
    print("🔍 Тестирование с реальным пользователем...")
    print(f"Base URL: {base_url}")
    print("=" * 50)
    
    # Тест 1: Найдем существующего пользователя
    print("1. Поиск существующего пользователя...")
    try:
        response = requests.get(f"{base_url}/v1/users/me?telegram_id=943454866", verify=False, timeout=10)
        print(f"   Статус: {response.status_code}")
        if response.status_code == 200:
            user_data = response.json()
            print(f"   Пользователь найден: {user_data.get('first_name', 'Unknown')}")
            user_id = user_data.get('id')
            telegram_id = user_data.get('telegram_id')
            print(f"   ID: {user_id}, Telegram ID: {telegram_id}")
        else:
            print(f"   Пользователь не найден: {response.text}")
            return
    except Exception as e:
        print(f"   Ошибка: {e}")
        return
    
    # Тест 2: Создание приглашения
    print("\n2. Создание приглашения...")
    try:
        response = requests.post(f"{base_url}/v1/invitations/generate?inviter_telegram_id={telegram_id}", verify=False, timeout=10)
        print(f"   Статус: {response.status_code}")
        if response.status_code == 200:
            invite_data = response.json()
            print(f"   Приглашение создано!")
            print(f"   Код: {invite_data.get('code')}")
            print(f"   Срок действия: {invite_data.get('expires_at')}")
            invite_code = invite_data.get('code')
        else:
            print(f"   Ошибка создания приглашения: {response.text}")
            return
    except Exception as e:
        print(f"   Ошибка: {e}")
        return
    
    # Тест 3: Получение информации о приглашении
    print("\n3. Получение информации о приглашении...")
    try:
        response = requests.get(f"{base_url}/v1/invitations/{invite_code}", verify=False, timeout=10)
        print(f"   Статус: {response.status_code}")
        if response.status_code == 200:
            info_data = response.json()
            print(f"   Информация получена!")
            print(f"   Приглашающий: {info_data.get('inviter_name')}")
            print(f"   Действительно: {info_data.get('is_valid')}")
        else:
            print(f"   Ошибка получения информации: {response.text}")
    except Exception as e:
        print(f"   Ошибка: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Тестирование завершено!")

if __name__ == "__main__":
    test_with_real_user()

