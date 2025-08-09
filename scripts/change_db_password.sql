-- ===========================================
-- СКРИПТ СМЕНЫ ПАРОЛЕЙ БАЗЫ ДАННЫХ
-- ===========================================

-- ИНСТРУКЦИЯ:
-- 1. Подключитесь к PostgreSQL как суперпользователь
-- 2. Замените НОВЫЙ_СИЛЬНЫЙ_ПАРОЛЬ на реальный пароль
-- 3. Выполните этот скрипт
-- 4. Обновите DATABASE_URL в .env файле

-- Создаем нового пользователя с сильным паролем
DROP USER IF EXISTS pair_helper_prod;
CREATE USER pair_helper_prod WITH PASSWORD 'НОВЫЙ_СИЛЬНЫЙ_ПАРОЛЬ';

-- Даем все необходимые права
GRANT ALL PRIVILEGES ON DATABASE pair_helper TO pair_helper_prod;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO pair_helper_prod;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO pair_helper_prod;
GRANT ALL PRIVILEGES ON SCHEMA public TO pair_helper_prod;

-- Даем права на будущие таблицы
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO pair_helper_prod;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO pair_helper_prod;

-- Удаляем старого небезопасного пользователя (ОСТОРОЖНО!)
-- Раскомментируйте после проверки, что новый пользователь работает
-- DROP USER IF EXISTS admin;

-- Проверяем права нового пользователя
SELECT 
    r.rolname,
    r.rolsuper,
    r.rolinherit,
    r.rolcreaterole,
    r.rolcreatedb,
    r.rolcanlogin,
    r.rolreplication
FROM pg_roles r 
WHERE r.rolname = 'pair_helper_prod';

-- Показываем права на базу данных
SELECT 
    d.datname as "Database",
    pg_catalog.pg_get_userbyid(d.datdba) as "Owner",
    pg_catalog.array_to_string(d.datacl, E'\n') AS "Access privileges"
FROM pg_catalog.pg_database d
WHERE d.datname = 'pair_helper'
ORDER BY 1;

