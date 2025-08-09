FROM node:18-alpine as dependencies

WORKDIR /app

# Копирование файлов зависимостей (только package.json и package-lock.json для кеша)
COPY package*.json ./

# Установка зависимостей (включая dev для сборки)
RUN npm ci

# Build stage
FROM node:18-alpine as build

WORKDIR /app

# Копируем node_modules из предыдущего stage
COPY --from=dependencies /app/node_modules ./node_modules
COPY package*.json ./

# Копирование исходного кода
COPY . .

# Сборка приложения
RUN npm run build

# Production stage (serve static, no nginx)
FROM node:18-alpine as runtime

WORKDIR /app

# Копируем собранный билд
COPY --from=build /app/dist ./dist

# Устанавливаем статический сервер
RUN npm i -g serve@14

# Открываем порт
EXPOSE 3000

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

# Запуск SPA сервера с выводом маркера билда в логи
CMD ["sh", "-c", "echo $BUILD_MARKER; echo BUILD_DATE=$BUILD_DATE BUILD_ID=$BUILD_ID; serve -s dist -l 3000"]