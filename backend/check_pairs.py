#!/usr/bin/env python3
"""
Скрипт для проверки существующих пар в базе данных
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models import Pair, User

def check_pairs():
    """Проверяет существующие пары в базе данных"""
    db = SessionLocal()
    
    try:
        # Получаем все активные пары
        pairs = db.query(Pair).filter(Pair.status == "active").all()
        
        print(f"Найдено {len(pairs)} активных пар:")
        print("-" * 50)
        
        for pair in pairs:
            user1 = db.query(User).filter(User.id == pair.user1_id).first()
            user2 = db.query(User).filter(User.id == pair.user2_id).first()
            
            print(f"Pair ID: {pair.id}")
            print(f"User1: {user1.first_name} (ID: {user1.id}, Telegram: {user1.telegram_id})")
            print(f"User2: {user2.first_name} (ID: {user2.id}, Telegram: {user2.telegram_id})")
            print(f"Created: {pair.created_at}")
            print("-" * 30)
        
        if not pairs:
            print("Активных пар не найдено!")
            
    except Exception as e:
        print(f"Ошибка при проверке пар: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_pairs()
