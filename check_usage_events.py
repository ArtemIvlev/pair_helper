#!/usr/bin/env python3
"""
Проверка таблицы usage_events
"""

import os
import sys
sys.path.append('backend')

from backend.app.core.database import SessionLocal
from backend.app.models.analytics import UsageEvent
from sqlalchemy import desc, func
from datetime import datetime, timezone

def check_usage_events():
    """Проверяем записи в таблице usage_events"""
    db = SessionLocal()
    try:
        print("📊 Проверка таблицы usage_events...")
        print("=" * 60)
        
        # Общая статистика
        total_count = db.query(UsageEvent).count()
        print(f"📈 Всего записей: {total_count}")
        
        if total_count == 0:
            print("⚠️ Таблица пуста!")
            return
        
        # Статистика по telegram_id
        null_count = db.query(UsageEvent).filter(UsageEvent.telegram_id.is_(None)).count()
        non_null_count = total_count - null_count
        
        print(f"✅ С telegram_id: {non_null_count}")
        print(f"❌ Без telegram_id: {null_count}")
        print(f"📊 Процент заполненности: {(non_null_count/total_count*100):.1f}%" if total_count > 0 else "0%")
        
        # Последние 10 записей
        print("\n📋 Последние 10 записей:")
        print("-" * 60)
        recent_events = db.query(UsageEvent).order_by(desc(UsageEvent.ts)).limit(10).all()
        
        for event in recent_events:
            print(f"ID: {event.id:4d} | Time: {event.ts} | Method: {event.method:6s} | Route: {event.route:30s} | Telegram ID: {event.telegram_id}")
        
        # Статистика по времени
        print("\n⏰ Статистика по времени:")
        print("-" * 60)
        
        # Записи за последний час
        now = datetime.now(timezone.utc)
        one_hour_ago = now.replace(tzinfo=None) - timedelta(hours=1)
        
        recent_count = db.query(UsageEvent).filter(UsageEvent.ts >= one_hour_ago).count()
        recent_with_telegram = db.query(UsageEvent).filter(
            UsageEvent.ts >= one_hour_ago,
            UsageEvent.telegram_id.isnot(None)
        ).count()
        
        print(f"🕐 За последний час: {recent_count} записей")
        print(f"✅ С telegram_id: {recent_with_telegram}")
        print(f"❌ Без telegram_id: {recent_count - recent_with_telegram}")
        
        if recent_count > 0:
            print(f"📊 Процент заполненности (час): {(recent_with_telegram/recent_count*100):.1f}%")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    from datetime import timedelta
    check_usage_events()
