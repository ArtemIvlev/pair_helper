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
from app.models import Question, Ritual
from app.models.ritual import PeriodicityEnum

# Демо-вопросы с номерами и категориями
DEMO_QUESTIONS = [
    (1, "Что сегодня заставило тебя улыбнуться?", "Эмоции"),
    (2, "О чём ты мечтаешь больше всего?", "Мечты"),
    (3, "Что бы ты хотел изменить в себе?", "Саморазвитие"),
    (4, "Какой твой любимый способ проводить время вместе?", "Отношения"),
    (5, "Что тебя вдохновляет?", "Мотивация"),
    (6, "О чём ты думаешь перед сном?", "Размышления"),
    (7, "Что бы ты хотел узнать о своём партнёре?", "Отношения"),
    (8, "Какой твой самый счастливый момент в отношениях?", "Отношения"),
    (9, "Что тебя беспокоит сейчас?", "Переживания"),
    (10, "Какой комплимент ты хотел бы услышать?", "Эмоции"),
    (11, "Что ты ценишь в своём партнёре больше всего?", "Отношения"),
    (12, "Какой твой любимый способ выражать любовь?", "Отношения"),
    (13, "Что бы ты хотел улучшить в отношениях?", "Отношения"),
    (14, "Какой твой самый смелый поступок?", "Жизненный опыт"),
    (15, "Что тебя успокаивает в трудные моменты?", "Поддержка"),
    (16, "Какой твой любимый способ начинать день?", "Привычки"),
    (17, "Что бы ты хотел попробовать вместе?", "Планы"),
    (18, "Какой твой самый важный урок в жизни?", "Жизненный опыт"),
    (19, "Что тебя мотивирует?", "Мотивация"),
    (20, "Какой твой любимый способ заботиться о себе?", "Забота о себе"),
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

def seed_questions(db: Session):
    """Загружает демо-вопросы"""
    print("Загружаем демо-вопросы...")
    
    for number, text, category in DEMO_QUESTIONS:
        existing = db.query(Question).filter(
            Question.number == number
        ).first()
        
        if not existing:
            question = Question(
                number=number,
                text=text,
                category=category
            )
            db.add(question)
            print(f"Добавлен вопрос #{number}: {text[:50]}...")
    
    db.commit()
    print(f"Загружено {len(DEMO_QUESTIONS)} вопросов")

def seed_default_rituals(db: Session):
    """Загружает демо-ритуалы (пропускаем, так как нужна пара)"""
    print("Пропускаем загрузку ритуалов - нужна активная пара")
    print("Ритуалы будут создаваться автоматически при создании пары")

def main():
    """Основная функция загрузки данных"""
    db = SessionLocal()
    
    try:
        seed_questions(db)
        seed_default_rituals(db)
        print("Демо-данные успешно загружены!")
        
    except Exception as e:
        print(f"Ошибка при загрузке данных: {e}")
        db.rollback()
        
    finally:
        db.close()

if __name__ == "__main__":
    main()
