from datetime import datetime, timedelta
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.core.database import get_db
from app.models import User, Pair, Mood, Appreciation, Ritual, RitualCheck, CalendarEvent, EmotionNote, UserAnswer, PairDailyQuestion, TuneAnswer, PairDailyTuneQuestion
from app.schemas.pair import PairWeeklyActivity, PairActivityItem

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/pair/{pair_id}/weekly-activity", response_model=PairWeeklyActivity)
def get_pair_weekly_activity_internal(
    pair_id: int,
    week_start: str = Query(..., description="Дата начала недели в формате YYYY-MM-DD"),
    db: Session = Depends(get_db)
):
    """Внутренний API для получения активности пары за неделю (без аутентификации Telegram)"""
    
    # Находим пару по ID
    pair = db.query(Pair).filter(
        Pair.id == pair_id,
        Pair.status == "active"
    ).first()
    
    if not pair:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Активная пара не найдена"
        )
    
    logger.info(f"Processing pair_id={pair_id}, found pair: user1={pair.user1_id}, user2={pair.user2_id}")
    
    # Парсим дату начала недели
    try:
        start_date = datetime.strptime(week_start, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный формат даты. Используйте YYYY-MM-DD"
        )
    
    end_date = start_date + timedelta(days=6)
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())
    
    # Загружаем данные пользователей пары
    user1 = db.query(User).filter(User.id == pair.user1_id).first()
    user2 = db.query(User).filter(User.id == pair.user2_id).first()
    
    activities = []
    
    # 1. Настроения (Mood)
    moods = db.query(Mood).filter(
        Mood.user_id.in_([pair.user1_id, pair.user2_id]),
        Mood.date >= start_datetime,
        Mood.date <= end_datetime
    ).order_by(Mood.date).all()
    
    mood_names = {
        "joyful": "радостное",
        "calm": "спокойное", 
        "tired": "уставшее",
        "anxious": "тревожное",
        "sad": "грустное",
        "irritable": "раздражительное",
        "grateful": "благодарное"
    }
    
    for mood in moods:
        mood_user = user1 if mood.user_id == pair.user1_id else user2
        mood_name = mood_names.get(mood.mood_code, mood.mood_code)
        activities.append(PairActivityItem(
            date=mood.date.strftime("%Y-%m-%d"),
            type="mood",
            title=f"Настроение: {mood_name}",
            description=mood.note or f"{mood_user.first_name} отметил настроение как {mood_name}",
            user_name=mood_user.first_name,
            timestamp=mood.date
        ))
    
    # 2. Благодарности (Appreciation)
    appreciations = db.query(Appreciation).filter(
        Appreciation.user_id.in_([pair.user1_id, pair.user2_id]),
        Appreciation.date >= start_datetime,
        Appreciation.date <= end_datetime
    ).order_by(Appreciation.date).all()
    
    for appreciation in appreciations:
        app_user = user1 if appreciation.user_id == pair.user1_id else user2
        activities.append(PairActivityItem(
            date=appreciation.date.strftime("%Y-%m-%d"),
            type="appreciation",
            title="Благодарность",
            description=appreciation.text,
            user_name=app_user.first_name,
            timestamp=appreciation.date
        ))
    
    # 3. Ритуалы (Ritual)
    ritual_checks = db.query(RitualCheck).join(Ritual).filter(
        Ritual.pair_id == pair.id,
        RitualCheck.date >= start_datetime,
        RitualCheck.date <= end_datetime,
        RitualCheck.done == True
    ).order_by(RitualCheck.date).all()
    
    for check in ritual_checks:
        check_user = user1 if check.user_id == pair.user1_id else user2
        ritual_title = check.ritual.title or "Ритуал без названия"
        activities.append(PairActivityItem(
            date=check.date.strftime("%Y-%m-%d"),
            type="ritual",
            title=f"Ритуал выполнен: {ritual_title}",
            description=f"{check_user.first_name} выполнил ритуал '{ritual_title}'",
            user_name=check_user.first_name,
            timestamp=check.date
        ))
    
    # 4. События календаря (Calendar)
    calendar_events = db.query(CalendarEvent).filter(
        CalendarEvent.pair_id == pair.id,
        CalendarEvent.date >= start_datetime,
        CalendarEvent.date <= end_datetime
    ).order_by(CalendarEvent.date).all()
    
    for event in calendar_events:
        event_user = user1 if event.user_id == pair.user1_id else user2 if event.user_id == pair.user2_id else None
        user_text = f" ({event_user.first_name})" if event_user else ""
        event_title = event.title or "Событие без названия"
        event_description = event.description or "Без описания"
        activities.append(PairActivityItem(
            date=event.date.strftime("%Y-%m-%d"),
            type="calendar",
            title=f"Событие: {event_title}",
            description=f"{event_description}{user_text}",
            user_name=event_user.first_name if event_user else "Общее",
            timestamp=event.date
        ))
    
    # 5. Эмоциональные заметки (EmotionNote)
    emotion_notes = db.query(EmotionNote).filter(
        EmotionNote.pair_id == pair.id,
        EmotionNote.date >= start_datetime,
        EmotionNote.date <= end_datetime
    ).order_by(EmotionNote.date).all()
    
    for note in emotion_notes:
        note_user = user1 if note.user_id == pair.user1_id else user2
        activities.append(PairActivityItem(
            date=note.date.strftime("%Y-%m-%d"),
            type="emotion_note",
            title="Эмоциональная заметка",
            description=note.text,
            user_name=note_user.first_name,
            timestamp=note.date
        ))
    
    # 6. Ответы на вопросы (Question)
    question_answers = db.query(UserAnswer).join(
        PairDailyQuestion, 
        UserAnswer.question_id == PairDailyQuestion.question_id
    ).filter(
        PairDailyQuestion.pair_id == pair.id,
        UserAnswer.created_at >= start_datetime,
        UserAnswer.created_at <= end_datetime
    ).order_by(UserAnswer.created_at).all()
    
    for answer in question_answers:
        answer_user = user1 if answer.user_id == pair.user1_id else user2
        question_text = answer.question.text or "Вопрос без текста"
        activities.append(PairActivityItem(
            date=answer.created_at.strftime("%Y-%m-%d"),
            type="question",
            title=f"Ответ на вопрос: {question_text[:50]}...",
            description=answer.answer_text,
            user_name=answer_user.first_name,
            timestamp=answer.created_at
        ))
    
    # 7. Ответы на вопросы сонастройки (Tune)
    # Группируем ответы по вопросам и датам
    tune_answers_by_question = {}
    
    tune_answers = db.query(TuneAnswer).join(
        PairDailyTuneQuestion,
        TuneAnswer.question_id == PairDailyTuneQuestion.question_id
    ).filter(
        TuneAnswer.pair_id == pair.id,  # Используем pair_id из TuneAnswer
        PairDailyTuneQuestion.pair_id == pair.id,
        TuneAnswer.created_at >= start_datetime,
        TuneAnswer.created_at <= end_datetime
    ).order_by(TuneAnswer.created_at).all()
    
    logger.info(f"Found {len(tune_answers)} tune answers for pair_id={pair.id}")
    
    for answer in tune_answers:
        question_key = f"{answer.question_id}_{answer.created_at.strftime('%Y-%m-%d')}"
        if question_key not in tune_answers_by_question:
            tune_answers_by_question[question_key] = {
                'question': answer.question,
                'date': answer.created_at,
                'answers': []
            }
        tune_answers_by_question[question_key]['answers'].append(answer)
    
    # Создаем активности для каждого вопроса сонастройки
    for question_key, data in tune_answers_by_question.items():
        question = data['question']
        answers = data['answers']
        date = data['date']
        
        # Получаем правильный текст вопроса
        question_text_self = question.text_about_self or question.text or "Вопрос о себе"
        question_text_partner = question.text_about_partner or question.text or "Вопрос о партнере"
        
        # Отладочная информация о вопросе
        logger.info(f"Tune question debug - question_id={question.id}, type={question.question_type}, options=[{question.option1}, {question.option2}, {question.option3}, {question.option4}]")
        
        # Группируем ответы по пользователям
        user1_self_answer = None
        user1_partner_answer = None
        user2_self_answer = None
        user2_partner_answer = None
        
        for answer in answers:
            if answer.author_user_id == pair.user1_id:
                if answer.subject_user_id == pair.user1_id:  # о себе
                    user1_self_answer = answer
                else:  # о партнере
                    user1_partner_answer = answer
            else:  # user2
                if answer.subject_user_id == pair.user2_id:  # о себе
                    user2_self_answer = answer
                else:  # о партнере
                    user2_partner_answer = answer
        
        # Функция для получения текста ответа
        def get_answer_text(answer):
            # Для MCQ вопросов всегда используем selected_option
            if answer.selected_option is not None:
                options = [question.option1, question.option2, question.option3, question.option4]
                # Фильтруем None значения
                valid_options = [opt for opt in options if opt]
                if 0 <= answer.selected_option < len(valid_options):
                    return valid_options[answer.selected_option]
                else:
                    return f"Вариант {answer.selected_option + 1}"
            
            # Для текстовых вопросов используем answer_text
            if answer.answer_text and answer.answer_text.strip():
                return answer.answer_text
            
            return "Ответ не указан"
        
        # Формируем описание
        description_parts = []
        
        if user1_self_answer:
            answer_text = get_answer_text(user1_self_answer)
            # Отладочная информация
            logger.info(f"Tune answer debug - user1_self: answer_text='{user1_self_answer.answer_text}', selected_option={user1_self_answer.selected_option}, result='{answer_text}'")
            description_parts.append(f"{user1.first_name} о себе: {answer_text}")
        if user2_partner_answer:
            answer_text = get_answer_text(user2_partner_answer)
            logger.info(f"Tune answer debug - user2_partner: answer_text='{user2_partner_answer.answer_text}', selected_option={user2_partner_answer.selected_option}, result='{answer_text}'")
            description_parts.append(f"{user2.first_name} думал о {user1.first_name}: {answer_text}")
        if user2_self_answer:
            answer_text = get_answer_text(user2_self_answer)
            logger.info(f"Tune answer debug - user2_self: answer_text='{user2_self_answer.answer_text}', selected_option={user2_self_answer.selected_option}, result='{answer_text}'")
            description_parts.append(f"{user2.first_name} о себе: {answer_text}")
        if user1_partner_answer:
            answer_text = get_answer_text(user1_partner_answer)
            logger.info(f"Tune answer debug - user1_partner: answer_text='{user1_partner_answer.answer_text}', selected_option={user1_partner_answer.selected_option}, result='{answer_text}'")
            description_parts.append(f"{user1.first_name} думал о {user2.first_name}: {answer_text}")
        
        description = " | ".join(description_parts)
        
        # Используем основной текст вопроса для заголовка
        main_question_text = question.text or question_text_self or "Вопрос сонастройки"
        
        activities.append(PairActivityItem(
            date=date.strftime("%Y-%m-%d"),
            type="tune",
            title=f"Сонастройка: {main_question_text[:50]}...",
            description=description,
            user_name="Оба партнера",
            timestamp=date
        ))
    
    # Сортируем все активности по времени
    activities.sort(key=lambda x: x.timestamp)
    
    # Создаем сводку
    activity_counts = {}
    for activity in activities:
        activity_counts[activity.type] = activity_counts.get(activity.type, 0) + 1
    
    summary_parts = []
    if activity_counts.get("mood", 0) > 0:
        summary_parts.append(f"{activity_counts['mood']} настроений")
    if activity_counts.get("appreciation", 0) > 0:
        summary_parts.append(f"{activity_counts['appreciation']} благодарностей")
    if activity_counts.get("ritual", 0) > 0:
        summary_parts.append(f"{activity_counts['ritual']} выполненных ритуалов")
    if activity_counts.get("calendar", 0) > 0:
        summary_parts.append(f"{activity_counts['calendar']} событий")
    if activity_counts.get("emotion_note", 0) > 0:
        summary_parts.append(f"{activity_counts['emotion_note']} эмоциональных заметок")
    if activity_counts.get("question", 0) > 0:
        summary_parts.append(f"{activity_counts['question']} ответов на вопросы")
    if activity_counts.get("tune", 0) > 0:
        summary_parts.append(f"{activity_counts['tune']} ответов на сонастройку")
    
    if summary_parts:
        summary = f"За неделю: {', '.join(summary_parts)}"
    else:
        summary = "За эту неделю активность не найдена"
    
    return PairWeeklyActivity(
        pair_id=pair.id,
        user1_name=user1.first_name,
        user2_name=user2.first_name,
        week_start=start_date.strftime("%Y-%m-%d"),
        week_end=end_date.strftime("%Y-%m-%d"),
        activities=activities,
        summary=summary
    )
