#!/usr/bin/env python3
"""
Тестовый скрипт для проверки API weekly-activity
"""

import requests
import json
from datetime import datetime, timedelta

# Конфигурация
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/v1/internal/pair/1/weekly-activity"  # Используем pair_id=1 для теста

# Тестовые данные
PAIR_ID = 1  # Замените на реальный ID пары из базы данных
WEEK_START = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

def test_weekly_activity():
    """Тестирует внутренний endpoint weekly-activity"""
    
    params = {
        "week_start": WEEK_START
    }
    
    print(f"Тестируем внутренний API: {API_URL}")
    print(f"Параметры: {params}")
    print("-" * 50)
    
    try:
        response = requests.get(API_URL, params=params)
        
        print(f"Статус ответа: {response.status_code}")
        print(f"Заголовки ответа: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("Успешный ответ:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # Анализируем данные
            print("\n" + "="*50)
            print("АНАЛИЗ ДАННЫХ:")
            print(f"Пара: {data.get('user1_name', 'N/A')} и {data.get('user2_name', 'N/A')}")
            print(f"Период: {data.get('week_start', 'N/A')} - {data.get('week_end', 'N/A')}")
            print(f"Сводка: {data.get('summary', 'N/A')}")
            print(f"Количество активностей: {len(data.get('activities', []))}")
            
            # Группируем активности по типам
            activity_types = {}
            for activity in data.get('activities', []):
                activity_type = activity.get('type', 'unknown')
                if activity_type not in activity_types:
                    activity_types[activity_type] = 0
                activity_types[activity_type] += 1
            
            print("\nАктивности по типам:")
            for activity_type, count in activity_types.items():
                print(f"  {activity_type}: {count}")
                
        else:
            print(f"Ошибка: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("Ошибка подключения. Убедитесь, что сервер запущен на http://localhost:8000")
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")

if __name__ == "__main__":
    test_weekly_activity()
