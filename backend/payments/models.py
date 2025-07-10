from django.db import models
from projects.models import Project
from users.models import UserProfile

class Package(models.Model):
    PACKAGE_TYPE_CHOICES = [
        ('one_time', 'Разовый пакет'),
        ('subscription', 'Подписка'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='packages', verbose_name='Проект')
    name = models.CharField('Название пакета', max_length=255)
    package_type = models.CharField('Тип пакета', max_length=20, choices=PACKAGE_TYPE_CHOICES, default='one_time')
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    num_readings = models.PositiveIntegerField('Количество раскладов', null=True, blank=True)
    subscription_days = models.PositiveIntegerField('Дней подписки', null=True, blank=True)
    is_active = models.BooleanField('Активен', default=True)
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлен', auto_now=True)

    class Meta:
        verbose_name = 'Пакет'
        verbose_name_plural = 'Пакеты'
        unique_together = ('project', 'name')

    def __str__(self):
        return f"{self.name} ({self.project.name}) - {self.price}₽"

class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает оплаты'),
        ('processing', 'Обрабатывается'),
        ('completed', 'Оплачен'),
        ('failed', 'Ошибка'),
        ('cancelled', 'Отменен'),
    ]

    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='payments', verbose_name='Пользователь')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='payments', verbose_name='Проект')
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name='payments', verbose_name='Пакет')
    amount = models.DecimalField('Сумма', max_digits=10, decimal_places=2)
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='pending')
    external_id = models.CharField('Внешний ID платежа', max_length=255, blank=True, null=True)
    payment_url = models.URLField('Ссылка на оплату', blank=True, null=True)
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлен', auto_now=True)
    completed_at = models.DateTimeField('Оплачен', blank=True, null=True)

    class Meta:
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'
        ordering = ['-created_at']

    def __str__(self):
        return f"Платеж {self.id} - {self.user} ({self.amount}₽) - {self.get_status_display()}"

    def mark_as_completed(self):
        """Отмечает платеж как завершенный"""
        from django.utils import timezone
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()

    def mark_as_failed(self):
        """Отмечает платеж как неудачный"""
        self.status = 'failed'
        self.save()

    def mark_as_cancelled(self):
        """Отмечает платеж как отмененный"""
        self.status = 'cancelled'
        self.save()
