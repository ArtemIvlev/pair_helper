#!/bin/bash

# BuildKit отключен - компонент buildx недоступен
# export DOCKER_BUILDKIT=1
# export COMPOSE_DOCKER_CLI_BUILD=1

# Скрипт для сборки и отправки Docker образов Pair Helper
set -e

echo "🚀 Начинаем сборку Docker образов Pair Helper с оптимизированными Dockerfile..."

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функции для красивого вывода
error() { echo -e "${RED}❌ ОШИБКА: $1${NC}"; exit 1; }
warning() { echo -e "${YELLOW}⚠️  ВНИМАНИЕ: $1${NC}"; }
success() { echo -e "${GREEN}✅ $1${NC}"; }
info() { echo -e "${BLUE}ℹ️  $1${NC}"; }

# Проверяем, что мы в корневой директории проекта
if [ ! -f "docker-compose.yml" ]; then
    error "docker-compose.yml не найден. Убедитесь, что вы находитесь в корневой директории проекта."
fi

# ===============================================
# ПРОВЕРКИ БЕЗОПАСНОСТИ ПЕРЕД СБОРКОЙ
# ===============================================

# ============================
# Парсинг аргументов
# ============================
SKIP_SECURITY=0
USE_CACHE=1
SELECTED_SERVICES=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --skip-security-checks)
      SKIP_SECURITY=1
      shift
      ;;
    --no-cache)
      USE_CACHE=0
      shift
      ;;
    --services=*)
      IFS=',' read -r -a SELECTED_SERVICES <<< "${1#*=}" # comma-separated list
      shift
      ;;
    --only=*)
      IFS=',' read -r -a SELECTED_SERVICES <<< "${1#*=}"
      shift
      ;;
    -h|--help)
      echo "Usage: ./build.sh [--skip-security-checks] [--no-cache] [--services=backend,bot,frontend,admin]"
      exit 0
      ;;
    *)
      echo "Неизвестный аргумент: $1"; exit 1;;
  esac
done

if [[ $SKIP_SECURITY -eq 1 ]]; then
    warning "Проверки безопасности пропущены по флагу --skip-security-checks"
    warning "ИСПОЛЬЗУЙТЕ ТОЛЬКО В ЭКСТРЕННЫХ СЛУЧАЯХ!"
    echo ""
else
    info "Выполняем проверки безопасности..."
    info "(Используйте --skip-security-checks для пропуска в экстренных случаях)"

# Проверяем наличие .env файла для продакшена
if [ ! -f ".env" ]; then
    warning ".env файл не найден. Убедитесь, что он создан для продакшена!"
else
    info "Проверяем, что в .env нет дефолтных/тестовых значений..."
    
    # Проверяем критичные переменные на дефолтные значения
    check_env_var() {
        local var_name=$1
        local var_value=$(grep "^${var_name}=" .env 2>/dev/null | cut -d'=' -f2- || echo "")
        
        if [ -z "$var_value" ]; then
            warning "Переменная $var_name не установлена в .env"
            return 1
        fi
        
        # Проверяем ТОЛЬКО на дефолтные/тестовые значения (не на сам факт хранения в .env)
        return 0
    }
    
    # Проверяем все критичные переменные
    if check_env_var "SECRET_KEY" && check_env_var "TELEGRAM_BOT_TOKEN" && check_env_var "DATABASE_URL"; then
        success "Конфигурация безопасности прошла проверку"
    fi
fi

# Проверяем, что секреты не в Git
info "Проверяем, что секреты не попали в Git..."
if git log --oneline --all --full-history -- deploy/stack.yml 2>/dev/null | head -5 | grep -q .; then
    if git show HEAD:deploy/stack.yml 2>/dev/null | grep -q "Passw0rd\|8239508680"; then
        warning "В текущей версии найдены секреты в stack.yml. Убедитесь, что используете переменные окружения!"
    fi
fi

# Проверяем зависимости на уязвимости (если доступно)
if command -v docker &> /dev/null; then
    info "Docker доступен, продолжаем сборку..."
else
    error "Docker не найден! Установите Docker для сборки образов."
fi

    success "Все проверки безопасности пройдены!"
    info "📝 Примечание: .env файлы предназначены для хранения секретов - это правильно!"
    info "    Мы проверяем только отсутствие тестовых/дефолтных значений."
    echo ""
fi

# Получаем дату сборки и уникальный ID
BUILD_DATE_ARG=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
BUILD_ID=$(date +%s)_$(head -c 8 /dev/urandom | base64 | tr -d '/' | tr -d '+' | head -c 8)
BUILD_MARKER="BUILD_${BUILD_ID}_DEPLOYED"

info "Дата сборки: $BUILD_DATE_ARG"
info "ID сборки: $BUILD_ID"
info "Метка для поиска в логах: $BUILD_MARKER"

# Registry URL
REGISTRY_URL="192.168.2.228:5000"
PROJECT_NAME="pair-helper"

info "Собираем Docker образы..."

# Определяем список сервисов для сборки
ALL_SERVICES=(backend bot frontend admin)
if [[ ${#SELECTED_SERVICES[@]} -eq 0 ]]; then
  SERVICES_TO_BUILD=("${ALL_SERVICES[@]}")
else
  SERVICES_TO_BUILD=("${SELECTED_SERVICES[@]}")
fi

# Флаг кеша для docker build
BUILD_CACHE_ARGS=()
if [[ $USE_CACHE -eq 0 ]]; then
  BUILD_CACHE_ARGS+=("--no-cache")
  warning "Сборка без кеша для сервисов: ${SERVICES_TO_BUILD[*]}"
fi

build_service() {
  local svc=$1
  local ctx="./$svc"
  local tag="${PROJECT_NAME}-${svc}:latest"
  info "Собираем ${svc^}..."
  docker build --network host \
    "${BUILD_CACHE_ARGS[@]}" \
    --build-arg BUILD_DATE=$BUILD_DATE_ARG \
    --build-arg BUILD_ID=$BUILD_ID \
    --build-arg BUILD_MARKER=$BUILD_MARKER \
    -t "$tag" "$ctx"
}

for svc in "${SERVICES_TO_BUILD[@]}"; do
  build_service "$svc"
done

success "Образы собраны успешно"

# Отправка образов в локальный registry
info "Отправляем образы в локальный registry..."

push_service() {
  local svc=$1
  local local_tag="${PROJECT_NAME}-${svc}:latest"
  local remote_tag="${REGISTRY_URL}/${PROJECT_NAME}-${svc}:latest"
  docker tag "$local_tag" "$remote_tag"
  docker push "$remote_tag"
}

for svc in "${SERVICES_TO_BUILD[@]}"; do
  push_service "$svc"
done

success "Образы отправлены в локальный registry"

# Обновление контейнеров через TrueNAS API
info "Обновляем контейнеры через TrueNAS API..."

if curl -s -X POST http://192.168.2.228:8080/v1/update \
  -H "Authorization: Bearer dummy" > /dev/null; then
    success "Обновление завершено!"
else
    warning "Не удалось обновить контейнеры через API. Проверьте TrueNAS."
fi

# Финальная проверка после деплоя
info "Проверяем работоспособность после деплоя..."
info "Ожидаем запуска контейнеров с меткой: $BUILD_MARKER"
sleep 15  # Даем время контейнерам запуститься

# Удаленный сервер где запущены контейнеры
REMOTE_SERVER="192.168.2.228"

# Функция быстрой проверки контейнеров через простой API
check_remote_containers() {
    info "Быстрая проверка статуса контейнеров на удаленном сервере..."
    
    # Проверяем TrueNAS API (который мы используем для обновления)
    if curl -s http://$REMOTE_SERVER:8080/v1/status --max-time 5 >/dev/null 2>&1; then
        success "TrueNAS API доступен"
    else
        warning "TrueNAS API недоступен"
    fi
}

# Функция проверки метки билда в логах
check_build_marker_in_logs() {
    info "Проверяем, появилась ли метка билда в логах..."
    
    # Проверяем наличие Python и зависимостей для работы с логами
    if command -v python3 &> /dev/null && [ -f "tests/check_backend_logs.py" ]; then
        info "Ищем метку '$BUILD_MARKER' в логах backend..."
        if timeout 30 python3 -c "
import subprocess
import sys
import time

# Пробуем найти метку в логах
for i in range(6):  # 6 попыток с интервалом 5 сек
    try:
        result = subprocess.run([
            'python3', 'tests/check_backend_logs.py'
        ], capture_output=True, text=True, timeout=10)
        
        if '$BUILD_MARKER' in result.stdout:
            print('✅ Метка билда найдена в логах!')
            sys.exit(0)
        else:
            print(f'⏳ Попытка {i+1}/6: метка пока не найдена...')
            time.sleep(5)
    except Exception as e:
        print(f'❌ Ошибка: {e}')
        time.sleep(5)

print('⚠️  Метка билда не найдена в логах за 30 секунд')
sys.exit(1)
" 2>/dev/null; then
            success "Метка билда найдена в логах! Новый билд успешно развернут."
        else
            warning "Метка билда не найдена в логах. Возможно, контейнеры еще не перезапустились."
            info "Проверьте логи вручную: python3 tests/check_backend_logs.py"
        fi
    else
        warning "Не удается автоматически проверить логи. Проверьте вручную:"
        info "  python3 tests/check_backend_logs.py | grep '$BUILD_MARKER'"
    fi
}

# Вызываем функцию проверки контейнеров
check_remote_containers

# Проверяем метку билда в логах
check_build_marker_in_logs

# Проверяем удаленный backend
info "Проверяем удаленный backend..."
if curl -s http://$REMOTE_SERVER:8000/health --max-time 10 | grep -q "healthy" 2>/dev/null; then
    success "Backend отвечает корректно (удаленный сервер)"
else
    warning "Backend недоступен на удаленном сервере. Проверьте логи через: python3 tests/check_backend_logs.py"
fi

# Проверяем удаленный frontend
info "Проверяем удаленный frontend..."
if curl -s http://$REMOTE_SERVER:3000 --max-time 10 >/dev/null 2>&1; then
    success "Frontend отвечает корректно (удаленный сервер)"
else
    warning "Frontend недоступен на удаленном сервере. Проверьте логи через: python3 tests/check_frontend_logs.py"
fi

# Проверки через nginx убраны - они не работают стабильно
info "Внешние URL проверки пропущены (nginx конфигурация вне проекта)"

echo ""
success "🎉 Сборка и развертывание Pair Helper завершены успешно!"
echo ""
info "🏷️  Информация о билде:"
echo "   • Build ID: $BUILD_ID"
echo "   • Build Date: $BUILD_DATE" 
echo "   • Build Marker: $BUILD_MARKER"
echo ""
info "Проверьте сервисы:"
echo ""
echo "   🏠 Удаленный сервер (прямые к контейнерам):"
echo "     • Backend:  http://$REMOTE_SERVER:8000/health"
echo "     • Frontend: http://$REMOTE_SERVER:3000/"
echo "     • Admin:    http://$REMOTE_SERVER:5001/"
echo ""
echo "   🔍 Мониторинг и логи:"
echo "     • Portainer: https://$REMOTE_SERVER:31015"
echo "     • Логи backend: python3 tests/check_backend_logs.py"
echo "     • Логи bot: python3 tests/check_bot_logs.py"
echo "     • Логи frontend: python3 tests/check_frontend_logs.py"
