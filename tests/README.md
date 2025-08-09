# 🧪 Pair Helper Auto Tests

Система автотестирования для приложения Pair Helper, которая проверяет:
- ✅ Работу API endpoints
- ✅ Статус Docker контейнеров
- ✅ Логи приложений через Portainer API
- ✅ Систему регистрации пользователей
- ✅ Систему приглашений

## 📋 Что тестируется

### 1. API Health Check
- Проверка доступности API
- Проверка документации API

### 2. Container Status
- Статус всех контейнеров (backend, frontend, bot, admin)
- Проверка что все контейнеры запущены

### 3. User Registration
- Регистрация тестового пользователя
- Проверка создания пользователя в базе

### 4. Invitation System
- Создание приглашения
- Проверка информации о приглашении

### 5. Container Logs
- Анализ логов всех контейнеров
- Поиск ошибок и исключений

## 🚀 Запуск тестов

### Быстрый запуск
```bash
./run_auto_tests.sh
```

### Ручной запуск
```bash
cd tests
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python run_tests.py
```

## ⚙️ Конфигурация

Настройки тестов находятся в файле `config.py`:

```python
class TestConfig:
    # API URLs
    API_BASE_URL = "https://gallery.homoludens.photos/pulse_of_pair/api"
    FRONTEND_URL = "https://gallery.homoludens.photos/pulse_of_pair"
    
    # Portainer API
    PORTAINER_URL = "https://192.168.2.228:31015"
    PORTAINER_USERNAME = "admin"
    PORTAINER_PASSWORD = "admin"
```

### Переменные окружения

**ВАЖНО**: Для работы с Portainer API нужны учетные данные!

1. Скопируйте пример файла:
```bash
cd tests
cp env.example .env
```

2. Отредактируйте файл `.env` и укажите ваши данные:
```env
# Portainer credentials (ОБЯЗАТЕЛЬНО!)
PORTAINER_USERNAME=your_portainer_username
PORTAINER_PASSWORD=your_portainer_password

# API URLs (опционально)
API_BASE_URL=https://gallery.homoludens.photos/pulse_of_pair/api
FRONTEND_URL=https://gallery.homoludens.photos/pulse_of_pair
```

3. Или установите переменные окружения:
```bash
export PORTAINER_USERNAME=your_username
export PORTAINER_PASSWORD=your_password
```

## 📊 Отчеты

После выполнения тестов создается JSON отчет с временной меткой:
- `test_report_YYYYMMDD_HHMMSS.json`

Отчет содержит:
- Результаты всех тестов
- Детальную информацию об ошибках
- Статистику успешности
- Логи контейнеров (если есть ошибки)

## 🔧 Структура проекта

```
tests/
├── __init__.py
├── config.py              # Конфигурация тестов
├── portainer_client.py    # Клиент для Portainer API
├── api_client.py          # Клиент для тестирования API
├── auto_tester.py         # Основной класс тестера
├── run_tests.py           # Скрипт запуска тестов
├── requirements.txt       # Зависимости Python
└── README.md             # Эта документация
```

## 🐛 Устранение неполадок

### Ошибка аутентификации в Portainer
- Проверьте правильность логина/пароля
- Убедитесь что Portainer доступен по указанному URL

### Ошибки API
- Проверьте что все контейнеры запущены
- Убедитесь что API доступен по указанному URL

### Ошибки SSL
- Тесты настроены для работы с self-signed сертификатами
- Если нужны строгие проверки SSL, измените `verify=False` на `True`

## 📈 Мониторинг

Рекомендуется запускать тесты:
- После каждого деплоя
- Ежедневно для мониторинга
- При подозрении на проблемы

Можно настроить cron для автоматического запуска:

```bash
# Ежедневно в 9:00
0 9 * * * /path/to/pair_helper/run_auto_tests.sh
```
