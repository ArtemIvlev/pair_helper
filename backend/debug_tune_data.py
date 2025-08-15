#!/usr/bin/env python3
"""
Скрипт для отладки данных сонастройки в базе
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models import TuneAnswer, TuneQuizQuestion, PairDailyTuneQuestion, Pair

def debug_tune_data():
    """Отлаживает данные сонастройки в базе"""
    db = SessionLocal()
    
    try:
        # Получаем все ответы сонастройки
        tune_answers = db.query(TuneAnswer).all()
        
        print(f"Найдено {len(tune_answers)} ответов сонастройки:")
        print("=" * 80)
        
        for answer in tune_answers:
            question = db.query(TuneQuizQuestion).filter(TuneQuizQuestion.id == answer.question_id).first()
            
            print(f"Ответ ID: {answer.id}")
            print(f"  Вопрос ID: {answer.question_id}")
            print(f"  Тип вопроса: {question.question_type if question else 'N/A'}")
            print(f"  Автор: {answer.author_user_id}")
            print(f"  О ком: {answer.subject_user_id}")
            print(f"  answer_text: '{answer.answer_text}'")
            print(f"  selected_option: {answer.selected_option}")
            
            if question:
                print(f"  Варианты ответов:")
                print(f"    option1: '{question.option1}'")
                print(f"    option2: '{question.option2}'")
                print(f"    option3: '{question.option3}'")
                print(f"    option4: '{question.option4}'")
                
                # Пробуем получить текст ответа
                if answer.answer_text and answer.answer_text.strip():
                    result_text = answer.answer_text
                elif answer.selected_option is not None:
                    options = [question.option1, question.option2, question.option3, question.option4]
                    valid_options = [opt for opt in options if opt]
                    if 0 <= answer.selected_option < len(valid_options):
                        result_text = valid_options[answer.selected_option]
                    else:
                        result_text = f"Вариант {answer.selected_option + 1}"
                else:
                    result_text = "Ответ не указан"
                
                print(f"  Результат: '{result_text}'")
            
            print("-" * 40)
        
        # Также проверим вопросы
        print("\n" + "=" * 80)
        print("ВОПРОСЫ СОНАНСТРОЙКИ:")
        
        questions = db.query(TuneQuizQuestion).all()
        for question in questions:
            print(f"Вопрос ID: {question.id}")
            print(f"  Тип: {question.question_type}")
            print(f"  Текст: '{question.text}'")
            print(f"  О себе: '{question.text_about_self}'")
            print(f"  О партнере: '{question.text_about_partner}'")
            print(f"  Варианты: [{question.option1}, {question.option2}, {question.option3}, {question.option4}]")
            print("-" * 40)
            
    except Exception as e:
        print(f"Ошибка при отладке: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    debug_tune_data()
