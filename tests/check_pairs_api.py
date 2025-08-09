#!/usr/bin/env python3
"""
Скрипт для проверки пар через API Pair Helper
"""

import requests
import json
from urllib3.exceptions import InsecureRequestWarning
import urllib3

# Отключаем предупреждения о SSL
urllib3.disable_warnings(InsecureRequestWarning)

def main():
    print("🔍 Проверка пар через API Pair Helper...")
    print("=" * 60)
    
    # API URL
    api_url = "http://192.168.2.228:8000/api/v1"
    
    try:
        # Проверяем пары
        print("1. Получение списка пар...")
        response = requests.get(f"{api_url}/pair", verify=False, timeout=10)
        
        if response.status_code == 200:
            pairs = response.json()
            print(f"✅ Найдено пар: {len(pairs)}")
            
            for i, pair in enumerate(pairs, 1):
                print(f"   Пара {i}:")
                print(f"     ID: {pair.get('id')}")
                print(f"     User1 ID: {pair.get('user1_id')}")
                print(f"     User2 ID: {pair.get('user2_id')}")
                print(f"     Создана: {pair.get('created_at')}")
                print()
        else:
            print(f"❌ Ошибка получения пар: {response.status_code}")
            print(f"   Ответ: {response.text}")
        
        # Проверяем пользователей
        print("2. Получение списка пользователей...")
        response = requests.get(f"{api_url}/users", verify=False, timeout=10)
        
        if response.status_code == 200:
            users = response.json()
            print(f"✅ Найдено пользователей: {len(users)}")
            
            for i, user in enumerate(users, 1):
                print(f"   Пользователь {i}:")
                print(f"     ID: {user.get('id')}")
                print(f"     Telegram ID: {user.get('telegram_id')}")
                print(f"     Имя: {user.get('first_name')}")
                print(f"     Зарегистрирован: {user.get('created_at')}")
                print()
        else:
            print(f"❌ Ошибка получения пользователей: {response.status_code}")
            print(f"   Ответ: {response.text}")
        
        # Проверяем приглашения
        print("3. Получение списка приглашений...")
        response = requests.get(f"{api_url}/invitations/user/943454866", verify=False, timeout=10)
        
        if response.status_code == 200:
            invitations = response.json()
            print(f"✅ Найдено приглашений: {len(invitations)}")
            
            for i, invitation in enumerate(invitations, 1):
                print(f"   Приглашение {i}:")
                print(f"     ID: {invitation.get('id')}")
                print(f"     Код: {invitation.get('code')}")
                print(f"     Использовано: {invitation.get('is_used')}")
                print(f"     Приглашенный: {invitation.get('invitee_telegram_id')}")
                print(f"     Создано: {invitation.get('created_at')}")
                print(f"     Истекает: {invitation.get('expires_at')}")
                print()
        else:
            print(f"❌ Ошибка получения приглашений: {response.status_code}")
            print(f"   Ответ: {response.text}")
            
    except Exception as e:
        print(f"❌ Ошибка при проверке API: {e}")
    
    print("✅ Проверка завершена!")

if __name__ == "__main__":
    main()
