# Настройка Grafana алерта на HTTP 500 ошибки

## Обзор
Этот алерт будет отслеживать HTTP 500 ошибки в таблице `usage_events` и отправлять уведомления при обнаружении проблем.

## Настройка в Grafana

### 1. Создание Alert Rule

1. Откройте Grafana
2. Перейдите в **Alerting** → **Alert Rules**
3. Нажмите **New Alert Rule**

### 2. Настройка Query

**Query A:**
```sql
SELECT COUNT(*) as error_count
FROM usage_events 
WHERE status = 500 
  AND ts >= NOW() - INTERVAL '5 minutes'
```

**DataSource:** PostgreSQL (pair_helper_db)
**Query Type:** SQL

### 3. Настройка Alert Rule

- **Name:** HTTP 500 Errors Alert
- **For:** 1m (алерт срабатывает после 1 минуты)
- **Condition:** `A > 1` (больше 1 ошибки за 5 минут)

### 4. Настройка уведомлений

#### Telegram уведомление:
1. В **Contact points** создайте новый contact point
2. **Type:** Telegram
3. **Bot Token:** Ваш Telegram bot token
4. **Chat ID:** ID чата для уведомлений
5. **Message Template:**
```
🚨 HTTP 500 Errors detected!

Route: {{ .Route }}
Count: {{ .Count }}
Time: {{ .Time }}

Check logs immediately!
```

### 5. Создание Dashboard

Создайте дашборд с панелями:

#### Панель 1: Количество ошибок 500
```sql
SELECT COUNT(*) as error_count
FROM usage_events 
WHERE status = 500 
  AND ts >= NOW() - INTERVAL '5 minutes'
```

#### Панель 2: Ошибки по маршрутам
```sql
SELECT 
    route,
    COUNT(*) as error_count
FROM usage_events 
WHERE status = 500 
  AND ts >= NOW() - INTERVAL '1 hour'
GROUP BY route 
ORDER BY error_count DESC 
LIMIT 10
```

#### Панель 3: График ошибок
```sql
SELECT 
    DATE_TRUNC('minute', ts) as time_bucket,
    COUNT(*) as error_count
FROM usage_events 
WHERE status = 500 
  AND ts >= NOW() - INTERVAL '1 hour'
GROUP BY DATE_TRUNC('minute', ts)
ORDER BY time_bucket
```

## Преимущества

✅ **Быстрое обнаружение проблем** - алерт срабатывает через 1 минуту  
✅ **Детальная информация** - показывает маршрут и количество ошибок  
✅ **Telegram уведомления** - мгновенные уведомления в чат  
✅ **Исторические данные** - графики для анализа трендов  

## Настройка порогов

- **Warning:** > 1 ошибка за 5 минут
- **Critical:** > 5 ошибок за 5 минут
- **Emergency:** > 10 ошибок за 5 минут

## Мониторинг

После настройки алерта вы будете получать уведомления о:
- Ошибках регистрации пользователей
- Проблемах с базой данных
- Ошибках API endpoints
- Любых других HTTP 500 ошибках
