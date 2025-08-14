-- Запрос для Grafana алерта на HTTP 500 ошибки
-- Используется в Alert Rule

-- Количество ошибок 500 за последние 5 минут
SELECT COUNT(*) as error_count
FROM usage_events 
WHERE status = 500 
  AND ts >= NOW() - INTERVAL '5 minutes';

-- Дополнительные запросы для дашборда:

-- 1. Ошибки по маршрутам за последний час
SELECT 
    route,
    COUNT(*) as error_count,
    MAX(ts) as last_error_time
FROM usage_events 
WHERE status = 500 
  AND ts >= NOW() - INTERVAL '1 hour'
GROUP BY route 
ORDER BY error_count DESC 
LIMIT 10;

-- 2. График ошибок по времени (для timeseries панели)
SELECT 
    DATE_TRUNC('minute', ts) as time_bucket,
    COUNT(*) as error_count
FROM usage_events 
WHERE status = 500 
  AND ts >= NOW() - INTERVAL '1 hour'
GROUP BY DATE_TRUNC('minute', ts)
ORDER BY time_bucket;

-- 3. Детали последних ошибок
SELECT 
    ts,
    method,
    route,
    telegram_id,
    duration_ms
FROM usage_events 
WHERE status = 500 
  AND ts >= NOW() - INTERVAL '30 minutes'
ORDER BY ts DESC 
LIMIT 20;

-- 4. Статистика по методам HTTP
SELECT 
    method,
    COUNT(*) as error_count
FROM usage_events 
WHERE status = 500 
  AND ts >= NOW() - INTERVAL '1 hour'
GROUP BY method 
ORDER BY error_count DESC;
