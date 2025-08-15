# Changelog: Создание внутреннего API для активности пары

## Обзор изменений

Создана новая категория внутренних API для использования без аутентификации Telegram, с защитой от внешнего доступа.

## Новые файлы

### 1. `app/api/api_v1/endpoints/internal.py`
- Новый роутер для внутренних API
- Endpoint `GET /api/v1/internal/pair/{pair_id}/weekly-activity`
- Получение активности пары по ID пары (без Telegram аутентификации)

### 2. `app/middleware/internal_api.py`
- Middleware для защиты внутренних API
- Проверка IP адресов (только локальные и внутренние сети)
- Логирование попыток доступа

### 3. `docs/weekly_activity_api.md`
- Обновленная документация для внутреннего API
- Информация о безопасности и ограничениях доступа

### 4. `test_weekly_activity.py`
- Обновлен для работы с новым внутренним API
- Убрана зависимость от Telegram ID

### 5. `example_weekly_activity.py`
- Обновлен для работы с новым внутренним API
- Использует pair_id вместо telegram_id

### 6. `README_weekly_activity.md`
- Обновлен с информацией о внутреннем API
- Добавлена информация о безопасности

## Измененные файлы

### 1. `app/api/api_v1/api.py`
- Добавлен импорт и подключение internal роутера
- Новый префикс `/internal` с тегом "internal"

### 2. `app/api/api_v1/endpoints/pair.py`
- Удален endpoint `/weekly-activity`
- Убраны неиспользуемые импорты
- Очищен от кода активности пары

### 3. `app/main.py`
- Добавлен InternalAPIMiddleware
- Middleware добавлен в цепочку обработки запросов

## API Endpoints

### Новый внутренний endpoint
```
GET /api/v1/internal/pair/{pair_id}/weekly-activity?week_start=YYYY-MM-DD
```

### Удаленный endpoint
```
GET /api/v1/pair/weekly-activity?week_start=YYYY-MM-DD
```

## Безопасность

### Разрешенные сети
- `127.0.0.1` (localhost)
- `::1` (localhost IPv6)
- `192.168.*` (локальные сети)
- `10.*` (внутренние сети)
- `172.16-18.*` (Docker сети)

### Защита
- Middleware проверяет IP адрес каждого запроса к `/api/v1/internal/*`
- Логирование всех попыток доступа
- HTTP 403 Forbidden для неразрешенных IP

## Использование

### Старый способ (удален)
```bash
curl -X GET "http://localhost:8000/api/v1/pair/weekly-activity?week_start=2024-01-15" \
  -H "X-Telegram-User-ID: 123456789"
```

### Новый способ (внутренний)
```bash
curl -X GET "http://localhost:8000/api/v1/internal/pair/1/weekly-activity?week_start=2024-01-15"
```

## Преимущества

1. **Безопасность**: Защита от внешнего доступа
2. **Простота**: Не требует Telegram аутентификации
3. **Гибкость**: Можно использовать pair_id напрямую
4. **Логирование**: Отслеживание всех попыток доступа
5. **Изоляция**: Внутренние API отделены от публичных

## Тестирование

```bash
# Тест внутреннего API
python3 test_weekly_activity.py

# Пример использования
python3 example_weekly_activity.py
```

## Swagger/OpenAPI

Внутренние API будут отображаться в Swagger UI с тегом "internal":
- URL: `http://localhost:8000/docs`
- Тег: "internal"
- Endpoint: `/api/v1/internal/pair/{pair_id}/weekly-activity`
