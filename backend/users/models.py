from django.db import models
from projects.models import Project

# Create your models here.

class UserProfile(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='users', verbose_name='Проект')
    telegram_user_id = models.BigIntegerField('Telegram user id', db_index=True)
    username = models.CharField('Telegram username', max_length=150, blank=True, null=True)
    balance = models.PositiveIntegerField('Баланс (раскладов)', default=5)
    subscription_start = models.DateField('Начало подписки', blank=True, null=True)
    subscription_end = models.DateField('Конец подписки', blank=True, null=True)
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлен', auto_now=True)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        unique_together = ('project', 'telegram_user_id')

    def __str__(self):
        return f"{self.username or self.telegram_user_id} ({self.project.name})"
