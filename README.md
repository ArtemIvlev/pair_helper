# Pair Helper - Telegram Web App для пар

Полнофункциональное приложение для пар с ежедневными практиками, календарем, ритуалами и аналитикой.

## Технологический стек

- **Backend**: Python, FastAPI
- **Бот**: aiogram v3 (асинхронный)
- **БД**: PostgreSQL + SQLAlchemy + Alembic
- **Frontend**: React (Vite) + Telegram WebApp SDK
- **Инфра**: Docker Compose

## Быстрый запуск

### Вариант 1: Локальный запуск (рекомендуется для разработки)

1. **Скопируйте переменные окружения:**
   ```bash
   cp env.example .env
   ```

2. **Настройте .env файл:**
   ```bash
   # Добавьте токен бота
   TELEGRAM_BOT_TOKEN=8239508680:AAG9iWlwHfm_wpfjtvm08JdEo26RaDOSYyY
   
   # База данных уже настроена
   DATABASE_URL=postgresql://admin:Passw0rd@192.168.2.228:5432/pair_helper
   ```

3. **Установите зависимости backend:**
   ```bash
   cd backend
   pip3 install -r requirements.txt
   ```

4. **Создайте таблицы и загрузите демо-данные:**
   ```bash
   python3 create_tables.py
   PYTHONPATH=. python3 scripts/seed_data.py
   ```

5. **Запустите backend:**
   ```bash
   PYTHONPATH=. python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

6. **Установите зависимости frontend:**
   ```bash
   cd ../frontend
   npm install
   ```

7. **Запустите frontend:**
   ```bash
   npm run dev
   ```

### Вариант 2: Docker Compose

1. Скопируйте `.env.example` в `.env` и настройте переменные
2. Запустите через Docker Compose:

```bash
docker-compose up -d
```

3. Примените миграции:

```bash
docker-compose exec backend alembic upgrade head
```

4. Загрузите демо-данные:

```bash
docker-compose exec backend python scripts/seed_data.py
```

## Структура проекта

```
pair_helper/
├── backend/                 # FastAPI приложение
│   ├── app/
│   │   ├── api/            # API эндпоинты
│   │   ├── core/           # Конфигурация, настройки
│   │   ├── models/         # SQLAlchemy модели
│   │   ├── schemas/        # Pydantic схемы
│   │   └── services/       # Бизнес-логика
│   ├── alembic/            # Миграции БД
│   └── tests/              # Тесты
├── bot/                    # Telegram бот
├── frontend/               # React Web App
├── nginx/                  # Nginx конфигурация
└── docker-compose.yml      # Docker Compose
```

## Настройка переменных окружения

Создайте файл `.env` на основе `.env.example`:

```bash
# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_WEBAPP_URL=https://your-domain.com

# Database
DATABASE_URL=postgresql://admin:Passw0rd@192.168.2.228:5432/pair_helper

# Security
SECRET_KEY=your_secret_key
```

⚠️ **Важно**: Файл `.env` содержит конфиденциальные данные и автоматически исключен из Git. Никогда не коммитьте файлы с паролями и токенами!

## API Документация

После запуска доступна по адресу: `http://localhost:8000/docs`

## Разработка

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Тесты
```bash
cd backend
pytest
```

## Миграции

```bash
# Создать новую миграцию
alembic revision --autogenerate -m "description"

# Применить миграции
alembic upgrade head

# Откатить миграцию
alembic downgrade -1
```

## Webhook настройка

Для продакшена настройте webhook:

```bash
curl -X POST "https://api.telegram.org/bot<BOT_TOKEN>/setWebhook" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://your-domain.com/webhook"}'
```

## Лицензия

MIT
