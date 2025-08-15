#!/usr/bin/env python3
"""
Тест исправленной сонастройки в внутреннем API
"""

import requests
import json
from datetime import datetime, timedelta

def test_tune_fix():
    """Тестирует исправленную сонастройку"""
    
    base_url = "http://localhost:8000"
    pair_id = 1
    week_start = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    
    print("🎯 ТЕСТ ИСПРАВЛЕННОЙ СОНАНСТРОЙКИ")
    print("=" * 60)
    
    try:
        response = requests.get(
            f"{base_url}/api/v1/internal/pair/{pair_id}/weekly-activity",
            params={"week_start": week_start}
        )
        
        print(f"Статус: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Ищем активности сонастройки
            tune_activities = [a for a in data['activities'] if a['type'] == 'tune']
            
            print(f"Найдено активностей сонастройки: {len(tune_activities)}")
            print()
            
            for i, activity in enumerate(tune_activities, 1):
                print(f"🎵 Сонастройка #{i}:")
                print(f"   Дата: {activity['date']}")
                print(f"   Вопрос: {activity['title']}")
                print(f"   Ответы:")
                
                # Разбиваем описание на части
                description = activity['description']
                if " | " in description:
                    parts = description.split(" | ")
                    for part in parts:
                        print(f"     • {part}")
                else:
                    print(f"     • {description}")
                print()
                
        else:
            print(f"Ошибка: {response.text}")
            
    except Exception as e:
        print(f"Исключение: {e}")

if __name__ == "__main__":
    test_tune_fix()
