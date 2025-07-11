from django.db import models
from projects.models import Project
from users.models import UserProfile

class TarotDeck(models.Model):
    name = models.CharField('Название колоды', max_length=255)
    description = models.TextField('Описание', blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='decks', verbose_name='Проект')
    created_at = models.DateTimeField('Создана', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлена', auto_now=True)

    class Meta:
        verbose_name = 'Колода Таро'
        verbose_name_plural = 'Колоды Таро'
        unique_together = ('name', 'project')

    def __str__(self):
        return f"{self.name} ({self.project.name})"

class TarotCard(models.Model):
    deck = models.ForeignKey(TarotDeck, on_delete=models.CASCADE, related_name='cards', verbose_name='Колода')
    name = models.CharField('Название карты', max_length=255)
    image = models.ImageField('Изображение', upload_to='tarot/cards/', blank=True, null=True)
    meaning_upright = models.TextField('Значение (прямое)', blank=True)
    meaning_reversed = models.TextField('Значение (перевернутое)', blank=True)
    order = models.PositiveIntegerField('Порядок в колоде', default=0)

    class Meta:
        verbose_name = 'Карта Таро'
        verbose_name_plural = 'Карты Таро'
        unique_together = ('deck', 'name')
        ordering = ['deck', 'order']

    def __str__(self):
        return f"{self.name} ({self.deck.name})"

class TarotSpread(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='spreads', verbose_name='Проект')
    name = models.CharField('Название расклада', max_length=255)
    description = models.TextField('Описание', blank=True)
    num_cards = models.PositiveIntegerField('Количество карт')
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлен', auto_now=True)

    class Meta:
        verbose_name = 'Расклад Таро'
        verbose_name_plural = 'Расклады Таро'
        unique_together = ('project', 'name')

    def __str__(self):
        return f"{self.name} ({self.project.name})"

class Interpretation(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='interpretations', verbose_name='Пользователь')
    spread = models.ForeignKey(TarotSpread, on_delete=models.CASCADE, related_name='interpretations', verbose_name='Расклад')
    cards = models.ManyToManyField(TarotCard, verbose_name='Карты')
    ai_response = models.TextField('AI-ответ')
    user_question = models.TextField('Вопрос пользователя', blank=True, null=True)
    created_at = models.DateTimeField('Дата', auto_now_add=True)

    class Meta:
        verbose_name = 'Интерпретация'
        verbose_name_plural = 'Интерпретации'
        ordering = ['-created_at']

    def __str__(self):
        return f"Интерпретация для {self.user} ({self.created_at:%Y-%m-%d %H:%M})"
