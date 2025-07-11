import os
from celery import Celery

# Устанавливаем переменную окружения для настроек Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings_production')

# Создаем экземпляр Celery
app = Celery('mystic_tarot')

# Используем строку здесь для того, чтобы worker не должен был сериализовать
# объект конфигурации для дочерних процессов.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Загружаем задачи из всех зарегистрированных приложений Django
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}') 