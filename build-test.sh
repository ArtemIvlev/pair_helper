#!/bin/bash

# Тестовый скрипт для сборки Docker образов Pair Helper (без отправки в registry)
set -e

echo "🚀 Начинаем тестовую сборку Docker образов Pair Helper..."

# Проверяем, что мы в корневой директории проекта
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Ошибка: docker-compose.yml не найден. Убедитесь, что вы находитесь в корневой директории проекта."
    exit 1
fi

# Получаем дату сборки
BUILD_DATE_ARG=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
echo "📅 Дата сборки: $BUILD_DATE_ARG"

PROJECT_NAME="pair-helper"

echo "📦 Собираем Docker образы..."

# Сборка Backend
echo "🔧 Собираем Backend..."
docker build --network host \
    --build-arg BUILD_DATE=$BUILD_DATE_ARG \
    -t ${PROJECT_NAME}-backend:latest ./backend

# Сборка Bot
echo "🤖 Собираем Bot..."
docker build --network host \
    --build-arg BUILD_DATE=$BUILD_DATE_ARG \
    -t ${PROJECT_NAME}-bot:latest ./bot

# Сборка Frontend
echo "🎨 Собираем Frontend..."
docker build --network host \
    --build-arg BUILD_DATE=$BUILD_DATE_ARG \
    -t ${PROJECT_NAME}-frontend:latest ./frontend

echo "✅ Образы собраны успешно!"

# Показываем информацию о собранных образах
echo "📋 Информация о собранных образах:"
docker images | grep ${PROJECT_NAME}

echo "🎉 Тестовая сборка завершена успешно!"
