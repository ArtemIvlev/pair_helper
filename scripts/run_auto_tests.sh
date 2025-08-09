#!/bin/bash

# Скрипт для запуска автотестов Pair Helper
# Проверяет API, статус контейнеров и логи через Portainer

set -e

echo "🧪 Запуск автотестов Pair Helper..."
echo "=================================="

# Проверяем наличие Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не найден. Установите Python 3.8+"
    exit 1
fi

# Переходим в директорию тестов
cd "$(dirname "$0")/tests"

# Устанавливаем зависимости если нужно
if [ ! -d "venv" ]; then
    echo "📦 Создание виртуального окружения..."
    python3 -m venv venv
fi

# Активируем виртуальное окружение
echo "🔧 Активация виртуального окружения..."
source venv/bin/activate

# Копируем .env файл если его нет
if [ ! -f ".env" ] && [ -f "env.example" ]; then
    echo "📝 Копирование env.example в .env..."
    cp env.example .env
    echo "⚠️  Отредактируйте файл .env и укажите ваши учетные данные Portainer!"
    echo "   Затем запустите тесты снова."
    exit 1
fi

# Устанавливаем зависимости
echo "📥 Установка зависимостей..."
pip install -r requirements.txt

# Запускаем тесты
echo "🚀 Запуск тестов..."
python run_tests.py

# Деактивируем виртуальное окружение
deactivate

echo "✅ Тесты завершены!"
