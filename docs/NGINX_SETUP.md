# 🌐 Настройка nginx для Pair Helper

## Обзор архитектуры

```
Интернет → nginx (HTTPS) → Docker контейнеры (HTTP)
                ↓
    ┌─────────────────────────────────┐
    │  nginx (внешний, порт 443)      │
    │  - SSL/TLS терминация           │
    │  - Rate limiting                │
    │  - Заголовки безопасности       │
    └─────────────────┬───────────────┘
                      │
    ┌─────────────────┴───────────────┐
    │     Docker контейнеры           │
    │  - Frontend (порт 3000)         │
    │  - Backend API (порт 8000)      │
    │  - Admin (порт 5001)            │
    └─────────────────────────────────┘
```

## 🚀 Быстрая настройка

### 1. Скопируйте конфигурацию
```bash
sudo cp docs/nginx-proxy-config.conf /etc/nginx/sites-available/pair-helper
```

### 2. Настройте SSL сертификаты
Отредактируйте в конфигурации:
```nginx
ssl_certificate /path/to/your/cert.pem;
ssl_private_key /path/to/your/key.pem;
```

### 3. Настройте IP ограничения для админки
```nginx
# В секции location /pulse_of_pair/admin/
allow 192.168.1.0/24;  # Ваша локальная сеть
allow YOUR_VPN_IP;     # Ваш VPN IP
deny all;
```

### 4. Активируйте конфигурацию
```bash
sudo ln -s /etc/nginx/sites-available/pair-helper /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 🔧 Важные настройки безопасности

### Rate Limiting
Конфигурация включает двухуровневую защиту:
- **nginx уровень**: 10 req/s для API, 30 req/s для приложения
- **Приложение**: 100 req/min дополнительно

### Заголовки безопасности
- `Strict-Transport-Security` - принудительный HTTPS
- `X-Frame-Options: DENY` - защита от clickjacking
- `X-Content-Type-Options: nosniff` - защита от MIME sniffing

### Проксирование
Обязательные заголовки для корректной работы:
```nginx
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
```

## 📊 Мониторинг

### Логи
```bash
# Доступ
tail -f /var/log/nginx/pair_helper_access.log

# Ошибки
tail -f /var/log/nginx/pair_helper_error.log

# Rate limiting
grep "limiting requests" /var/log/nginx/pair_helper_error.log
```

### Проверка работоспособности
```bash
# Проверка HTTPS
curl -I https://gallery.homoludens.photos/pulse_of_pair/

# Проверка API
curl -I https://gallery.homoludens.photos/pulse_of_pair/api/health

# Проверка заголовков безопасности
curl -I https://gallery.homoludens.photos/pulse_of_pair/ | grep -E "(Strict-Transport|X-Frame|X-Content)"
```

## ⚠️ Безопасность

### Обязательно настройте:
1. **SSL сертификаты** (Let's Encrypt рекомендуется)
2. **IP ограничения** для админки
3. **Firewall** на сервере
4. **Регулярное обновление** nginx

### Рекомендации:
- Используйте только TLS 1.2+
- Настройте автоматическое обновление сертификатов
- Мониторьте логи на подозрительную активность
- Регулярно проверяйте SSL конфигурацию

## 🔧 Устранение неполадок

### Приложение не отвечает
```bash
# Проверьте статус контейнеров
docker ps

# Проверьте логи nginx
sudo tail -f /var/log/nginx/error.log

# Проверьте доступность backend
curl -I http://localhost:8000/health
```

### SSL проблемы
```bash
# Проверьте сертификаты
openssl x509 -in /path/to/cert.pem -text -noout

# Тест SSL
openssl s_client -connect gallery.homoludens.photos:443
```

### Rate limiting срабатывает
```bash
# Посмотрите на rate limiting логи
grep "limiting requests" /var/log/nginx/error.log

# При необходимости увеличьте лимиты в конфигурации
```

## 📞 Поддержка

При проблемах проверьте:
1. Статус nginx: `systemctl status nginx`
2. Конфигурация: `nginx -t`
3. Логи: `/var/log/nginx/`
4. Статус контейнеров: `docker ps`
5. Доступность портов: `netstat -tlnp | grep -E "(3000|8000|5001)"`

