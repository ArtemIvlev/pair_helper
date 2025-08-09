#!/bin/bash

echo "🚀 Запуск Pair Helper..."

# Проверяем наличие .env файла
if [ ! -f .env ]; then
    echo "⚠️  Файл .env не найден. Копируем из примера..."
    cp env.example .env
    echo "📝 Отредактируйте .env файл и добавьте ваш TELEGRAM_BOT_TOKEN"
    echo "🔑 Получите токен у @BotFather в Telegram"
    exit 1
fi

# Запускаем Docker Compose
echo "🐳 Запускаем сервисы..."
docker-compose up -d

# Ждем запуска PostgreSQL
echo "⏳ Ждем запуска базы данных..."
sleep 10

# Применяем миграции
echo "🗄️  Применяем миграции..."
docker-compose exec -T backend alembic upgrade head

# Загружаем демо-данные
echo "📊 Загружаем демо-данные..."
docker-compose exec -T backend python scripts/seed_data.py

echo "✅ Pair Helper запущен!"
echo ""
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "🤖 Для настройки бота:"
echo "1. Получите токен у @BotFather"
echo "2. Добавьте его в .env файл"
echo "3. Перезапустите: docker-compose restart bot"
echo ""
echo "🛑 Для остановки: docker-compose down"
