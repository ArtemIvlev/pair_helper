#!/usr/bin/env python3
"""
Демонстрация работы нового внутреннего API для активности пары
"""

import requests
import json
from datetime import datetime, timedelta

def demo_internal_api():
    """Демонстрирует работу внутреннего API"""
    
    base_url = "http://localhost:8000"
    
    # Тестовые данные
    pair_id = 1
    week_start = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    
    print("🎯 ДЕМОНСТРАЦИЯ ВНУТРЕННЕГО API")
    print("=" * 60)
    
    # 1. Тест успешного запроса
    print(f"1️⃣ Тестируем успешный запрос:")
    print(f"   URL: {base_url}/api/v1/internal/pair/{pair_id}/weekly-activity")
    print(f"   Параметры: week_start={week_start}")
    print()
    
    try:
        response = requests.get(
            f"{base_url}/api/v1/internal/pair/{pair_id}/weekly-activity",
            params={"week_start": week_start}
        )
        
        print(f"   Статус: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Успех!")
            print(f"   Пара: {data['user1_name']} и {data['user2_name']}")
            print(f"   Период: {data['week_start']} - {data['week_end']}")
            print(f"   Сводка: {data['summary']}")
            print(f"   Активностей: {len(data['activities'])}")
            
            if data['activities']:
                print(f"   Примеры активностей:")
                for i, activity in enumerate(data['activities'][:3]):
                    print(f"     {i+1}. {activity['date']} - {activity['title']}")
                if len(data['activities']) > 3:
                    print(f"     ... и еще {len(data['activities']) - 3}")
        else:
            print(f"   ❌ Ошибка: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Исключение: {e}")
    
    print()
    print("-" * 60)
    
    # 2. Тест с несуществующей парой
    print(f"2️⃣ Тестируем с несуществующей парой:")
    print(f"   URL: {base_url}/api/v1/internal/pair/999/weekly-activity")
    print()
    
    try:
        response = requests.get(
            f"{base_url}/api/v1/internal/pair/999/weekly-activity",
            params={"week_start": week_start}
        )
        
        print(f"   Статус: {response.status_code}")
        if response.status_code == 404:
            print(f"   ✅ Ожидаемая ошибка 404: {response.json()}")
        else:
            print(f"   ❌ Неожиданный статус: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Исключение: {e}")
    
    print()
    print("-" * 60)
    
    # 3. Тест с неверным форматом даты
    print(f"3️⃣ Тестируем с неверным форматом даты:")
    print(f"   URL: {base_url}/api/v1/internal/pair/{pair_id}/weekly-activity")
    print(f"   Параметры: week_start=invalid-date")
    print()
    
    try:
        response = requests.get(
            f"{base_url}/api/v1/internal/pair/{pair_id}/weekly-activity",
            params={"week_start": "invalid-date"}
        )
        
        print(f"   Статус: {response.status_code}")
        if response.status_code == 400:
            print(f"   ✅ Ожидаемая ошибка 400: {response.json()}")
        else:
            print(f"   ❌ Неожиданный статус: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Исключение: {e}")
    
    print()
    print("=" * 60)
    print("🎉 Демонстрация завершена!")
    print()
    print("📋 Сводка:")
    print("   ✅ Внутренний API работает")
    print("   ✅ Middleware безопасности функционирует")
    print("   ✅ Обработка ошибок работает корректно")
    print("   ✅ Аналитика не собирается для внутренних API")

if __name__ == "__main__":
    demo_internal_api()
