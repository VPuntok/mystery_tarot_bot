# 🚀 Развертывание Mystic Tarot Bot на сервере

Это руководство поможет вам развернуть приложение Mystic Tarot Bot на сервере с использованием Docker.

## 📋 Требования

- **Сервер** с Ubuntu 20.04+ или CentOS 8+
- **Docker** 20.10+
- **Docker Compose** 2.0+
- **Минимум 2GB RAM** и **20GB свободного места**
- **Домен** (опционально, для production)

## 🛠️ Установка на сервере

### 1. Подготовка сервера

```bash
# Обновляем систему
sudo apt update && sudo apt upgrade -y

# Устанавливаем Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Добавляем пользователя в группу docker
sudo usermod -aG docker $USER

# Устанавливаем Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Перезагружаемся для применения изменений
sudo reboot
```

### 2. Клонирование проекта

```bash
# Клонируем репозиторий
git clone https://github.com/your-username/mystic_tarot_bot.git
cd mystic_tarot_bot

# Копируем файл с переменными окружения
cp env.example .env
```

### 3. Настройка переменных окружения

Отредактируйте файл `.env`:

```bash
nano .env
```

**Обязательные настройки:**
```env
# Django настройки
DEBUG=False
SECRET_KEY=your-super-secret-key-change-this-in-production
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# База данных
DB_PASSWORD=your-secure-password

# CORS
CORS_ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com
```

### 4. Развертывание

```bash
# Запускаем скрипт развертывания
./deploy.sh
```

## 🐳 Архитектура Docker

Приложение состоит из следующих контейнеров:

- **`db`** - PostgreSQL база данных
- **`redis`** - Redis для Celery
- **`backend`** - Django приложение
- **`celery`** - Celery worker для фоновых задач
- **`celery-beat`** - Celery beat для периодических задач
- **`nginx`** - Nginx веб-сервер

## 🔧 Конфигурация для Production

### 1. SSL сертификаты

Для production замените самоподписанный сертификат на Let's Encrypt:

```bash
# Устанавливаем Certbot
sudo apt install certbot python3-certbot-nginx

# Получаем сертификат
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Копируем сертификаты в папку nginx
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx/ssl/key.pem
```

### 2. Брандмауэр

```bash
# Открываем только необходимые порты
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### 3. Мониторинг

Добавьте мониторинг в `docker-compose.yml`:

```yaml
# Prometheus для мониторинга
prometheus:
  image: prom/prometheus
  ports:
    - "9090:9090"
  volumes:
    - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml

# Grafana для визуализации
grafana:
  image: grafana/grafana
  ports:
    - "3000:3000"
  environment:
    - GF_SECURITY_ADMIN_PASSWORD=your-grafana-password
```

## 📊 Управление приложением

### Основные команды

```bash
# Запуск всех сервисов
docker-compose up -d

# Остановка всех сервисов
docker-compose down

# Просмотр логов
docker-compose logs -f

# Просмотр логов конкретного сервиса
docker-compose logs -f backend

# Перезапуск сервиса
docker-compose restart backend

# Обновление приложения
git pull
docker-compose build --no-cache
docker-compose up -d
```

### Резервное копирование

```bash
# Создание резервной копии базы данных
docker-compose exec db pg_dump -U mystic_user mystic_tarot > backup_$(date +%Y%m%d_%H%M%S).sql

# Восстановление из резервной копии
docker-compose exec -T db psql -U mystic_user mystic_tarot < backup_file.sql
```

### Мониторинг и логи

```bash
# Проверка статуса сервисов
docker-compose ps

# Просмотр использования ресурсов
docker stats

# Проверка логов Django
docker-compose exec backend tail -f logs/django.log
```

## 🔒 Безопасность

### 1. Обновление SECRET_KEY

```python
# Генерируем новый SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 2. Настройка Django Admin

```bash
# Создание суперпользователя
docker-compose exec backend python manage.py createsuperuser
```

### 3. Ограничение доступа к API

Добавьте в `settings_production.py`:

```python
# Ограничение доступа к API
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    }
}
```

## 🚨 Устранение неполадок

### Проблемы с базой данных

```bash
# Проверка подключения к базе данных
docker-compose exec backend python manage.py dbshell

# Сброс миграций (осторожно!)
docker-compose exec backend python manage.py migrate --fake-initial
```

### Проблемы с Redis

```bash
# Проверка Redis
docker-compose exec redis redis-cli ping

# Очистка Redis
docker-compose exec redis redis-cli flushall
```

### Проблемы с Nginx

```bash
# Проверка конфигурации Nginx
docker-compose exec nginx nginx -t

# Перезагрузка Nginx
docker-compose exec nginx nginx -s reload
```

### Проблемы с Celery

```bash
# Проверка статуса Celery
docker-compose exec backend celery -A core inspect active

# Очистка очереди задач
docker-compose exec backend celery -A core purge
```

## 📈 Масштабирование

### Горизонтальное масштабирование

```bash
# Увеличение количества workers
docker-compose up -d --scale backend=3 --scale celery=2
```

### Вертикальное масштабирование

Добавьте в `docker-compose.yml`:

```yaml
backend:
  deploy:
    resources:
      limits:
        memory: 1G
        cpus: '0.5'
      reservations:
        memory: 512M
        cpus: '0.25'
```

## 🔄 CI/CD

### GitHub Actions

Создайте `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Server

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Deploy to server
        uses: appleboy/ssh-action@v0.1.5
        with:
          host: ${{ secrets.HOST }}
          username: ${{ secrets.USERNAME }}
          key: ${{ secrets.KEY }}
          script: |
            cd /path/to/mystic_tarot_bot
            git pull
            docker-compose build --no-cache
            docker-compose up -d
            docker-compose exec backend python manage.py migrate
            docker-compose exec backend python manage.py collectstatic --noinput
```

## 📞 Поддержка

При возникновении проблем:

1. Проверьте логи: `docker-compose logs -f`
2. Проверьте статус сервисов: `docker-compose ps`
3. Проверьте использование ресурсов: `docker stats`
4. Создайте issue в репозитории с подробным описанием проблемы

## 📚 Дополнительные ресурсы

- [Docker Documentation](https://docs.docker.com/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/)
- [Nginx Configuration](https://nginx.org/en/docs/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/) 