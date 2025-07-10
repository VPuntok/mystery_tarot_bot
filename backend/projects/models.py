from django.db import models
from django.contrib.postgres.fields import JSONField

class Project(models.Model):
    STATUS_CHOICES = [
        ('active', 'Активен'),
        ('inactive', 'Неактивен'),
    ]

    name = models.CharField('Название проекта', max_length=255)
    telegram_token = models.CharField('Telegram Bot Token', max_length=255, unique=True)
    design = models.JSONField('Дизайн-настройки', default=dict, blank=True)
    status = models.CharField('Статус', max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлен', auto_now=True)

    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'

    def __str__(self):
        return self.name
