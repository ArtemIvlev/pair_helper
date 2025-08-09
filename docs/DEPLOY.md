# 🚀 Деплой Pair Helper

## 📋 Обзор

Pair Helper состоит из 3 основных компонентов:
- **Backend** (FastAPI) - API сервер
- **Bot** (aiogram) - Telegram бот
- **Frontend** (React) - Telegram Web App

**Примечание:** PostgreSQL уже установлен на сервере `192.168.2.228:5432`

**Домен:** `https://gallery.homoludens.photos/pulse_of_pair`

## 🐳 Docker Registry

Образы собираются и отправляются в локальный registry:
```
192.168.2.228:5000
```

## 📦 Сборка и деплой

### 1. Тестовая сборка (локально)
```bash
./build-test.sh
```

### 2. Полная сборка и деплой
```bash
./build.sh
```

Этот скрипт:
- Собирает все Docker образы
- Отправляет их в registry `192.168.2.228:5000`
- Обновляет контейнеры через TrueNAS API

### 3. Ручной деплой через stack.yml
```bash
docker-compose -f deploy/stack.yml up -d
```

## 🔄 Автоматическое обновление

### Watchtower
Все контейнеры настроены для автоматического обновления через Watchtower:
- **Метка**: `com.centurylinklabs.watchtower.enable=true`
- **Период проверки**: настраивается в Watchtower
- **Обновление**: автоматическое при наличии новых образов в registry

### Ручное обновление
```bash
# Остановить старые контейнеры
docker-compose -f deploy/stack.yml down

# Запустить новые
docker-compose -f deploy/stack.yml up -d

# Применить миграции (если нужно)
docker-compose -f deploy/stack.yml exec pair-helper-backend alembic upgrade head
```

## 🔧 Конфигурация

### Переменные окружения

Основные переменные настраиваются в `deploy/stack.yml`:

- `DATABASE_URL` - подключение к PostgreSQL (192.168.2.228:5432)
- `TELEGRAM_BOT_TOKEN` - токен бота
- `SECRET_KEY` - секретный ключ для JWT
- `API_BASE_URL` - URL API сервера (https://gallery.homoludens.photos/pulse_of_pair/api)
- `VITE_API_BASE_URL` - URL API для frontend
- `TELEGRAM_WEBAPP_URL` - URL Web App для бота

### Порты

- **Backend**: 8000
- **Frontend**: 3000

### URL структура

- **Frontend**: `https://gallery.homoludens.photos/pulse_of_pair/`
- **API**: `https://gallery.homoludens.photos/pulse_of_pair/api/`
- **Telegram Web App**: `https://gallery.homoludens.photos/pulse_of_pair`

## 🗄️ База данных

PostgreSQL уже установлен на сервере:
- **Хост**: 192.168.2.228
- **Порт**: 5432
- **База**: `pair_helper`
- **Пользователь**: `admin`
- **Пароль**: `Passw0rd`

При первом запуске автоматически применяются миграции и загружаются демо-данные.

## 🌐 Nginx конфигурация

Используйте файл `nginx-config-example.conf` как шаблон для настройки nginx:

```bash
# Скопировать конфигурацию
sudo cp nginx-config-example.conf /etc/nginx/sites-available/pair-helper

# Создать символическую ссылку
sudo ln -s /etc/nginx/sites-available/pair-helper /etc/nginx/sites-enabled/

# Проверить конфигурацию
sudo nginx -t

# Перезагрузить nginx
sudo systemctl reload nginx
```

**Важно:** Не забудьте настроить SSL сертификаты и обновить пути в конфигурации nginx.

## 📊 Мониторинг

### Логи контейнеров
```bash
# Все сервисы
docker-compose -f deploy/stack.yml logs -f

# Конкретный сервис
docker-compose -f deploy/stack.yml logs -f pair-helper-backend
```

### Статус контейнеров
```bash
docker-compose -f deploy/stack.yml ps
```

### Проверка Watchtower
```bash
# Проверить логи Watchtower
docker logs watchtower

# Проверить статус обновлений
docker ps --filter "label=com.centurylinklabs.watchtower.enable=true"
```

## 🔒 Безопасность

### Production настройки

1. **Измените SECRET_KEY**:
   ```bash
   # Генерируем новый секретный ключ
   openssl rand -hex 32
   ```

2. **Настройте SSL** через nginx (см. nginx-config-example.conf)

3. **Ограничьте доступ** к базе данных

4. **Используйте переменные окружения** для чувствительных данных

### Проверка безопасности
```bash
# Проверка уязвимостей в образах
docker scan pair-helper-backend:latest
docker scan pair-helper-bot:latest
docker scan pair-helper-frontend:latest
```

## 🐛 Отладка

### Проверка подключения к базе
```bash
docker-compose -f deploy/stack.yml exec pair-helper-backend python check_db.py
```

### Проверка API
```bash
curl https://gallery.homoludens.photos/pulse_of_pair/api/health
```

### Проверка бота
```bash
docker-compose -f deploy/stack.yml logs pair-helper-bot
```

### Проверка frontend
```bash
curl https://gallery.homoludens.photos/pulse_of_pair/
```

## 📝 Примечания

- Все образы используют многоэтапную сборку для оптимизации размера
- Контейнеры запускаются от непривилегированных пользователей
- Используется сеть `pair_helper_network` для изоляции
- PostgreSQL уже установлен на сервере и не включается в stack
- Настроено автоматическое обновление через Watchtower
- Приложение доступно по адресу `https://gallery.homoludens.photos/pulse_of_pair`
