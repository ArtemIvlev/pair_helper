#!/usr/bin/env python3
"""
Пример использования API weekly-activity
"""

import requests
import json
from datetime import datetime, timedelta

def get_weekly_activity(pair_id: int, week_start: str, base_url: str = "http://localhost:8000"):
    """
    Получает активность пары за неделю (внутренний API)
    
    Args:
        pair_id: ID пары
        week_start: Дата начала недели в формате YYYY-MM-DD
        base_url: Базовый URL API
    
    Returns:
        dict: Данные активности пары
    """
    
    url = f"{base_url}/api/v1/internal/pair/{pair_id}/weekly-activity"
    params = {"week_start": week_start}
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса: {e}")
        return None

def format_activity_report(data):
    """
    Форматирует отчет об активности в читаемый вид
    
    Args:
        data: Данные активности от API
    """
    if not data:
        print("Нет данных для отображения")
        return
    
    print("=" * 60)
    print(f"ОТЧЕТ ОБ АКТИВНОСТИ ПАРЫ")
    print("=" * 60)
    print(f"Пара: {data['user1_name']} и {data['user2_name']}")
    print(f"Период: {data['week_start']} - {data['week_end']}")
    print(f"Сводка: {data['summary']}")
    print()
    
    if not data['activities']:
        print("За этот период активность не найдена.")
        return
    
    # Группируем активности по дням
    activities_by_day = {}
    for activity in data['activities']:
        day = activity['date']
        if day not in activities_by_day:
            activities_by_day[day] = []
        activities_by_day[day].append(activity)
    
    # Выводим активности по дням
    for day in sorted(activities_by_day.keys()):
        print(f"📅 {day}")
        print("-" * 40)
        
        for activity in activities_by_day[day]:
            # Эмодзи для разных типов активности
            emoji_map = {
                "mood": "😊",
                "appreciation": "🙏",
                "ritual": "✨",
                "calendar": "📅",
                "emotion_note": "💭",
                "question": "❓",
                "tune": "🎵"
            }
            
            emoji = emoji_map.get(activity['type'], "📝")
            time_str = activity['timestamp'].split('T')[1][:5] if 'T' in activity['timestamp'] else ""
            
            print(f"{emoji} {time_str} | {activity['user_name']}: {activity['title']}")
            if activity['description'] and len(activity['description']) > 50:
                print(f"   {activity['description'][:50]}...")
            elif activity['description']:
                print(f"   {activity['description']}")
            print()
    
    print("=" * 60)

def main():
    """Основная функция для демонстрации"""
    
    # Пример использования
    pair_id = 1  # Замените на реальный ID пары
    
    # Получаем активность за текущую неделю
    today = datetime.now()
    current_week_start = (today - timedelta(days=today.weekday())).strftime("%Y-%m-%d")
    
    print("Получение активности за текущую неделю...")
    current_week_data = get_weekly_activity(pair_id, current_week_start)
    format_activity_report(current_week_data)
    
    # Получаем активность за прошлую неделю
    last_week_start = (today - timedelta(days=today.weekday() + 7)).strftime("%Y-%m-%d")
    
    print("\n" + "="*60)
    print("Получение активности за прошлую неделю...")
    last_week_data = get_weekly_activity(pair_id, last_week_start)
    format_activity_report(last_week_data)

if __name__ == "__main__":
    main()
