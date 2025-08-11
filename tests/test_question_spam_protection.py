#!/usr/bin/env python3
"""
Тест защиты от спама в ежедневных вопросах
"""

import requests
import time
import json
from datetime import datetime

# Конфигурация
BASE_URL = "http://192.168.2.228:8000"
API_BASE = f"{BASE_URL}/api/v1"

def test_question_spam_protection():
    """Тестируем защиту от спама в уведомлениях ежедневных вопросов"""
    
    print("🧪 Тестируем защиту от спама в ежедневных вопросах...")
    
    # Тестовые данные (замените на реальные)
    test_user_token = "your_test_token_here"  # Нужен реальный токен пользователя
    
    headers = {
        "Authorization": f"Bearer {test_user_token}",
        "Content-Type": "application/json"
    }
    
    # Первый запрос - должен пройти успешно
    print("📤 Отправляем первое уведомление...")
    try:
        response = requests.post(
            f"{API_BASE}/questions/notify_partner",
            headers=headers
        )
        
        if response.status_code == 200:
            print("✅ Первое уведомление отправлено успешно")
        elif response.status_code == 400:
            print(f"⚠️ Первое уведомление: {response.json().get('detail', 'Ошибка')}")
        else:
            print(f"❌ Первое уведомление: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Ошибка при первом уведомлении: {e}")
    
    # Второй запрос сразу после первого - должен быть заблокирован
    print("📤 Отправляем второе уведомление (должно быть заблокировано)...")
    try:
        response = requests.post(
            f"{API_BASE}/questions/notify_partner",
            headers=headers
        )
        
        if response.status_code == 429:
            detail = response.json().get('detail', '')
            print(f"✅ Второе уведомление заблокировано: {detail}")
        elif response.status_code == 200:
            print("⚠️ Второе уведомление прошло (возможно, партнёр уже ответил)")
        else:
            print(f"❌ Неожиданный ответ: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Ошибка при втором уведомлении: {e}")
    
    print("\n📊 Проверяем логи для подтверждения...")
    print("💡 Для полного тестирования нужен реальный токен пользователя с парой")

if __name__ == "__main__":
    test_question_spam_protection()
