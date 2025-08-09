FROM python:3.11-slim as dependencies

# Создаем виртуальное окружение
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Копирование файлов зависимостей (только requirements.txt для кеша)
COPY requirements.txt .

# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Финальный stage
FROM python:3.11-slim

# Копируем виртуальное окружение из предыдущего stage
COPY --from=dependencies /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Создание пользователя без прав root
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Копирование кода приложения (этот слой будет пересобираться при изменении кода)
COPY . .

# Открытие порта
EXPOSE 5001

# Аргументы сборки (в самом конце чтобы не ломать кеш)
ARG BUILD_DATE
ARG BUILD_ID  
ARG BUILD_MARKER

# Метаданные образа
LABEL build_date="${BUILD_DATE}"
LABEL build_id="${BUILD_ID}"
LABEL build_marker="${BUILD_MARKER}"

# Переменные окружения для передачи в контейнер
ENV BUILD_DATE=${BUILD_DATE}
ENV BUILD_ID=${BUILD_ID}
ENV BUILD_MARKER=${BUILD_MARKER}

# Команда запуска
CMD ["python", "app.py"]