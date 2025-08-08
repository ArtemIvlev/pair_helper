# Безопасность Pair Helper

## Конфиденциальные данные

### Файлы, которые НЕ должны попадать в Git:

- `.env` - содержит все секреты и пароли
- `*.key`, `*.pem`, `*.p12` - сертификаты и ключи
- `api_keys.txt`, `tokens.json` - API ключи
- `database.ini`, `db_config.json` - конфигурация БД
- `secrets.*` - любые файлы с секретами

### Текущие настройки безопасности:

1. **База данных**: PostgreSQL на внешнем сервере `192.168.2.228`
2. **Пользователь БД**: `admin` (требует смены в продакшене)
3. **Пароль БД**: `Passw0rd` (требует смены в продакшене)

## Рекомендации для продакшена:

### 1. Смена паролей БД
```sql
-- Создать нового пользователя
CREATE USER pair_helper_user WITH PASSWORD 'strong_password_here';

-- Дать права на базу
GRANT ALL PRIVILEGES ON DATABASE pair_helper TO pair_helper_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO pair_helper_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO pair_helper_user;
```

### 2. Обновление .env
```bash
DATABASE_URL=postgresql://pair_helper_user:strong_password_here@192.168.2.228:5432/pair_helper
SECRET_KEY=your-super-secret-key-change-this-in-production
```

### 3. Настройка SSL для БД
```bash
# В DATABASE_URL добавить sslmode=require
DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require
```

### 4. Ограничение доступа к БД
- Настроить firewall на сервере БД
- Ограничить доступ только с IP адресов приложения
- Использовать VPN для подключения

## Проверка безопасности

Перед деплоем проверьте:

1. ✅ `.env` файл не в Git
2. ✅ Пароли достаточно сложные
3. ✅ SSL включен для БД
4. ✅ Firewall настроен
5. ✅ Логи не содержат паролей

## Мониторинг

- Регулярно проверяйте логи на утечки данных
- Мониторьте подключения к БД
- Обновляйте зависимости на предмет уязвимостей
