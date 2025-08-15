# Исправления ошибок в внутреннем API

## Проблемы и решения

### 1. Ошибка SQL JOIN
**Проблема**: SQLAlchemy не мог правильно выполнить JOIN между таблицами
```
ERROR: Don't know how to join to <Mapper at 0x7f87e1fa3590; PairDailyQuestion>
```

**Решение**: Добавлены явные условия JOIN
```python
# Было:
question_answers = db.query(UserAnswer).join(PairDailyQuestion).filter(...)

# Стало:
question_answers = db.query(UserAnswer).join(
    PairDailyQuestion, 
    UserAnswer.question_id == PairDailyQuestion.question_id
).filter(...)
```

### 2. Ошибка с NoneType в аналитике
**Проблема**: UsageAnalyticsMiddleware пытался обработать внутренние API
```
ERROR: 'NoneType' object is not subscriptable
```

**Решение**: Исключили внутренние API из сбора аналитики
```python
# Пропускаем внутренние API - они не нужны для аналитики пользователей
if request.url.path.startswith("/api/v1/internal"):
    return await call_next(request)
```

### 3. Ошибка с None в текстах вопросов
**Проблема**: Поля `text` в вопросах могут быть `None`
```
TypeError: 'NoneType' object is not subscriptable
```

**Решение**: Добавлены проверки на `None` для всех текстовых полей

#### Для обычных вопросов:
```python
# Было:
title=f"Ответ на вопрос: {answer.question.text[:50]}...",

# Стало:
question_text = answer.question.text or "Вопрос без текста"
title=f"Ответ на вопрос: {question_text[:50]}...",
```

#### Для вопросов сонастройки:
```python
# Было:
title=f"Сонастройка: {answer.question.text[:50]}...",

# Стало:
question_text = answer.question.text or "Вопрос без текста"
title=f"Сонастройка: {question_text[:50]}...",
```

#### Для событий календаря:
```python
# Было:
title=f"Событие: {event.title}",
description=f"{event.description or 'Без описания'}{user_text}",

# Стало:
event_title = event.title or "Событие без названия"
event_description = event.description or "Без описания"
title=f"Событие: {event_title}",
description=f"{event_description}{user_text}",
```

#### Для ритуалов:
```python
# Было:
title=f"Ритуал выполнен: {check.ritual.title}",
description=f"{check_user.first_name} выполнил ритуал '{check.ritual.title}'",

# Стало:
ritual_title = check.ritual.title or "Ритуал без названия"
title=f"Ритуал выполнен: {ritual_title}",
description=f"{check_user.first_name} выполнил ритуал '{ritual_title}'",
```

## Результат

✅ **Все ошибки исправлены**
✅ **API работает стабильно**
✅ **Обработка некорректных данных**
✅ **Логирование без ошибок**

### 4. Исправление отчета по сонастройке
**Проблема**: Отчет по сонастройке показывал ответы неправильно, не группировал по вопросам
```
Старый формат: отдельные записи для каждого ответа
```

**Решение**: Группировка ответов по вопросам с правильным форматированием
```python
# Группируем ответы по вопросам и датам
tune_answers_by_question = {}

# Формируем описание в формате:
# "Анна о себе: ответ | Иван думал об Анне: ответ | Иван о себе: ответ | Анна думала об Иване: ответ"
```

**Новый формат отчета**:
```
🎵 Сонастройка: Вопрос о том, как мы проводим время вместе...
   Ответы:
     • Анна о себе: Люблю проводить время дома
     • Иван думал об Анне: Думаю, она предпочитает активный отдых
     • Иван о себе: Мне нравится путешествовать
     • Анна думала об Иване: Он любит спокойный отдых
```

### 5. Исправление отображения ответов MCQ
**Проблема**: Для MCQ вопросов показывались идентификаторы вместо текстов ответов
```
"Артём о себе: 0 | Anna думал о Артём: 0"
```

**Решение**: Добавлена функция для получения правильного текста ответа
```python
def get_answer_text(answer):
    if answer.answer_text and answer.answer_text.strip():
        return answer.answer_text
    elif answer.selected_option is not None and question.question_type == "mcq":
        # Для MCQ вопросов получаем текст варианта
        options = [question.option1, question.option2, question.option3, question.option4]
        if 0 <= answer.selected_option < len(options) and options[answer.selected_option]:
            return options[answer.selected_option]
        else:
            return f"Вариант {answer.selected_option + 1}"
    else:
        return "Ответ не указан"
```

**Результат**: Теперь показываются тексты ответов вместо идентификаторов
```
"Артём о себе: Люблю проводить время дома | Anna думал о Артём: Думаю, он предпочитает активный отдых"
```

## Тестирование

API теперь корректно обрабатывает:
- Запросы с существующими парами
- Запросы с несуществующими парами (404)
- Запросы с неверным форматом даты (400)
- Данные с пустыми/отсутствующими текстовыми полями
- Внутренние запросы без сбора аналитики
- **Правильную группировку ответов сонастройки**
- **Корректное отображение текстов MCQ ответов**
