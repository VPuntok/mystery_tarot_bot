#!/bin/bash

# Скрипт для запуска Mystic Tarot Bot в режиме разработки

echo "🔧 Запуск в режиме разработки..."

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

# Останавливаем production контейнеры если они запущены
echo "🛑 Останавливаем production контейнеры..."
docker compose down 2>/dev/null || true

# Запускаем контейнеры для разработки
echo "🚀 Запускаем контейнеры для разработки..."
docker compose -f docker-compose.dev.yml up --build

echo ""
echo "✅ Приложение запущено в режиме разработки!"
echo ""
echo "🌐 Доступные URL:"
echo "   - Фронтенд: http://localhost:3000"
echo "   - Бэкенд API: http://localhost:8000/api/"
echo "   - Django Admin: http://localhost:8000/admin/"
echo "   - Swagger: http://localhost:8000/swagger/"
echo ""
echo "📋 Полезные команды:"
echo "   - Остановка: Ctrl+C"
echo "   - Просмотр логов: docker compose -f docker-compose.dev.yml logs -f"
echo "   - Перезапуск: ./dev.sh" 