#!/usr/bin/env python3
"""
Скрипт для загрузки демо-данных в базу
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Загружаем переменные окружения
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models import DailyQuestion, Ritual
from app.models.ritual import PeriodicityEnum

# Демо-вопросы дня
DAILY_QUESTIONS = [
    "Что сегодня заставило тебя улыбнуться?",
    "О чём ты мечтаешь больше всего?",
    "Что бы ты хотел изменить в себе?",
    "Какой твой любимый способ проводить время вместе?",
    "Что тебя вдохновляет?",
    "О чём ты думаешь перед сном?",
    "Что бы ты хотел узнать о своём партнёре?",
    "Какой твой самый счастливый момент в отношениях?",
    "Что тебя беспокоит сейчас?",
    "Какой комплимент ты хотел бы услышать?",
    "Что ты ценишь в своём партнёре больше всего?",
    "Какой твой любимый способ выражать любовь?",
    "Что бы ты хотел улучшить в отношениях?",
    "Какой твой самый смелый поступок?",
    "Что тебя успокаивает в трудные моменты?",
    "Какой твой любимый способ начинать день?",
    "Что бы ты хотел попробовать вместе?",
    "Какой твой самый важный урок в жизни?",
    "Что тебя мотивирует?",
    "Какой твой любимый способ заботиться о себе?",
]

# Демо-ритуалы
DEFAULT_RITUALS = [
    ("Утренний поцелуй", "Ежедневный ритуал начала дня", PeriodicityEnum.DAILY),
    ("Вечерние объятия", "Завершение дня в объятиях", PeriodicityEnum.DAILY),
    ("Совместный завтрак", "Начинать день вместе", PeriodicityEnum.DAILY),
    ("Прогулка перед сном", "Время для разговоров", PeriodicityEnum.DAILY),
    ("Совместное планирование", "Планируем неделю вместе", PeriodicityEnum.WEEKLY),
    ("Свидание выходного дня", "Особенное время для двоих", PeriodicityEnum.WEEKLY),
    ("Совместная готовка", "Готовим любимые блюда", PeriodicityEnum.WEEKLY),
    ("Вечер кино", "Смотрим фильмы вместе", PeriodicityEnum.WEEKLY),
    ("Совместная уборка", "Поддерживаем порядок вместе", PeriodicityEnum.WEEKLY),
    ("Время для хобби", "Занимаемся любимыми делами", PeriodicityEnum.WEEKLY),
]

def seed_daily_questions(db: Session):
    """Загружает демо-вопросы дня"""
    print("Загружаем демо-вопросы дня...")
    
    for question_text in DAILY_QUESTIONS:
        existing = db.query(DailyQuestion).filter(
            DailyQuestion.text == question_text
        ).first()
        
        if not existing:
            question = DailyQuestion(text=question_text)
            db.add(question)
            print(f"Добавлен вопрос: {question_text[:50]}...")
    
    db.commit()
    print(f"Загружено {len(DAILY_QUESTIONS)} вопросов дня")

def seed_default_rituals(db: Session):
    """Загружает демо-ритуалы (пропускаем, так как нужна пара)"""
    print("Пропускаем загрузку ритуалов - нужна активная пара")
    print("Ритуалы будут создаваться автоматически при создании пары")

def main():
    """Основная функция загрузки данных"""
    db = SessionLocal()
    
    try:
        seed_daily_questions(db)
        seed_default_rituals(db)
        print("Демо-данные успешно загружены!")
        
    except Exception as e:
        print(f"Ошибка при загрузке данных: {e}")
        db.rollback()
        
    finally:
        db.close()

if __name__ == "__main__":
    main()
