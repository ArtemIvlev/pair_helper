#!/usr/bin/env python3
"""
Скрипт для тестирования использования приглашения
"""

import requests
import json
from urllib3.exceptions import InsecureRequestWarning
import urllib3

# Отключаем предупреждения о SSL
urllib3.disable_warnings(InsecureRequestWarning)

def main():
    print("🧪 Тестирование использования приглашения...")
    print("=" * 60)
    
    # API URL
    api_url = "http://192.168.2.228:8000/api/v1"
    
    # Тестовые данные
    invite_code = "79dZfZ6FLCej8VKHUSDH0g"  # Последнее приглашение
    invitee_telegram_id = 158238656  # Второй пользователь
    
    try:
        print(f"1. Используем приглашение {invite_code} для пользователя {invitee_telegram_id}")
        
        response = requests.post(
            f"{api_url}/invitations/{invite_code}/use?invitee_telegram_id={invitee_telegram_id}",
            headers={'Content-Type': 'application/json'},
            verify=False,
            timeout=10
        )
        
        print(f"   Статус: {response.status_code}")
        print(f"   Ответ: {response.text}")
        
        if response.status_code == 200:
            print("✅ Приглашение успешно использовано!")
        else:
            print("❌ Ошибка использования приглашения")
            
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
    
    print("\n2. Проверяем статус приглашения...")
    try:
        response = requests.get(f"{api_url}/invitations/user/943454866", verify=False, timeout=10)
        
        if response.status_code == 200:
            invitations = response.json()
            for invitation in invitations:
                if invitation.get('code') == invite_code:
                    print(f"   Код: {invitation.get('code')}")
                    print(f"   Использовано: {invitation.get('is_used')}")
                    print(f"   Приглашенный: {invitation.get('invitee_telegram_id')}")
                    break
        else:
            print(f"❌ Ошибка получения приглашений: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Ошибка при проверке: {e}")
    
    print("\n✅ Тестирование завершено!")

if __name__ == "__main__":
    main()

