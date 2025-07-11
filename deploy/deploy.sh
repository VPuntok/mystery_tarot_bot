#!/bin/bash

# Скрипт для развертывания Mystic Tarot Bot на сервере

set -e

echo "🚀 Начинаем развертывание Mystic Tarot Bot..."

# Проверяем наличие Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен. Установите Docker и попробуйте снова."
    exit 1
fi

# Проверяем наличие docker compose
if ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose не установлен. Установите Docker Compose и попробуйте снова."
    exit 1
fi

# Проверяем наличие .env файла
if [ ! -f .env ]; then
    echo "⚠️  Файл .env не найден. Создаем из примера..."
    cp env.example .env
    echo "📝 Отредактируйте файл .env и запустите скрипт снова."
    exit 1
fi

# Создаем необходимые директории
echo "📁 Создаем необходимые директории..."
mkdir -p nginx/ssl
mkdir -p backend/logs
mkdir -p backend/static
mkdir -p backend/media

# Генерируем самоподписанный SSL сертификат для разработки
if [ ! -f nginx/ssl/cert.pem ] || [ ! -f nginx/ssl/key.pem ]; then
    echo "🔐 Генерируем самоподписанный SSL сертификат..."
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout nginx/ssl/key.pem \
        -out nginx/ssl/cert.pem \
        -subj "/C=RU/ST=State/L=City/O=Organization/CN=localhost"
fi

# Собираем и запускаем контейнеры
echo "🐳 Собираем и запускаем Docker контейнеры..."
docker compose down
docker compose build --no-cache
docker compose up -d

# Ждем запуска базы данных
echo "⏳ Ждем запуска базы данных..."
sleep 10

# Выполняем миграции
echo "🗄️  Выполняем миграции базы данных..."
docker compose exec backend python manage.py migrate

# Создаем суперпользователя (опционально)
read -p "🤔 Создать суперпользователя Django? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker compose exec backend python manage.py createsuperuser
fi

# Собираем статические файлы
echo "📦 Собираем статические файлы..."
docker compose exec backend python manage.py collectstatic --noinput

# Проверяем статус сервисов
echo "🔍 Проверяем статус сервисов..."
docker compose ps

echo ""
echo "✅ Развертывание завершено!"
echo ""
echo "🌐 Доступные URL:"
echo "   - Фронтенд: https://localhost"
echo "   - API: https://localhost/api/"
echo "   - Django Admin: https://localhost/admin/"
echo "   - Swagger: https://localhost/swagger/"
echo "   - Health Check: https://localhost/health/"
echo ""
echo "📋 Полезные команды:"
echo "   - Просмотр логов: docker compose logs -f"
echo "   - Остановка: docker compose down"
echo "   - Перезапуск: docker compose restart"
echo "   - Обновление: ./deploy.sh"
echo ""
echo "⚠️  Для production:"
echo "   1. Замените самоподписанный SSL сертификат на реальный"
echo "   2. Настройте домен в .env файле"
echo "   3. Измените SECRET_KEY на безопасный"
echo "   4. Настройте брандмауэр" 