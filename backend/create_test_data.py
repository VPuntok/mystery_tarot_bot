#!/usr/bin/env python
"""
Скрипт для создания тестовых данных
"""
import os
import sys
import django
from django.utils import timezone
from datetime import timedelta

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from projects.models import Project
from users.models import UserProfile
from tarot.models import TarotDeck, TarotCard, TarotSpread, Interpretation
from payments.models import Package, Payment

def create_test_data():
    """Создание тестовых данных"""
    print("Создание тестовых данных...")
    
    # 1. Создаем тестовый проект
    project, created = Project.objects.get_or_create(
        name="Mystic Tarot Bot",
        defaults={
            'telegram_token': 'test_token_123456',
            'status': 'active'
        }
    )
    print(f"Проект: {project.name} ({'создан' if created else 'уже существует'})")
    
    # 2. Создаем тестового пользователя
    user, created = UserProfile.objects.get_or_create(
        telegram_user_id=123456789,
        project=project,
        defaults={
            'username': 'test_user',
            'balance': 5,
            'subscription_start': timezone.now().date(),
            'subscription_end': timezone.now().date() + timedelta(days=30)
        }
    )
    print(f"Пользователь: {user.username} ({'создан' if created else 'уже существует'})")
    
    # 3. Создаем колоду карт
    deck, created = TarotDeck.objects.get_or_create(
        name="Классическая колода Таро",
        project=project,
        defaults={
            'description': 'Стандартная колода из 78 карт'
        }
    )
    print(f"Колода: {deck.name} ({'создана' if created else 'уже существует'})")
    
    # 4. Создаем карты Таро
    cards_data = [
        ("Шут", "Начало пути, невинность, спонтанность", "Безрассудство, риск, неопытность"),
        ("Маг", "Сила воли, мастерство, концентрация", "Манипуляция, неиспользованные возможности"),
        ("Верховная Жрица", "Интуиция, тайные знания, внутренняя мудрость", "Скрытые мотивы, поверхностность"),
        ("Императрица", "Плодородие, материнство, природа", "Зависимость, бесплодие, пустота"),
        ("Император", "Авторитет, структура, контроль", "Тирания, жесткость, доминирование"),
        ("Иерофант", "Традиция, духовность, образование", "Догматизм, ограниченность, невежество"),
        ("Влюбленные", "Любовь, гармония, выбор", "Дисгармония, неверность, нерешительность"),
        ("Колесница", "Победа, контроль, воля", "Потеря контроля, агрессия, поражение"),
        ("Сила", "Сила духа, мужество, влияние", "Слабость, неуверенность, отсутствие веры"),
        ("Отшельник", "Самоанализ, поиск, одиночество", "Изоляция, одиночество, отказ от помощи"),
    ]
    
    for i, (name, upright, reversed) in enumerate(cards_data):
        card, created = TarotCard.objects.get_or_create(
            name=name,
            deck=deck,
            defaults={
                'meaning_upright': upright,
                'meaning_reversed': reversed,
                'order': i + 1
            }
        )
        if created:
            print(f"Карта создана: {card.name}")
    
    # 5. Создаем расклады
    spreads_data = [
        ("Расклад одной карты", "Простое гадание на одну карту", 1),
        ("Расклад трех карт", "Прошлое, настоящее, будущее", 3),
        ("Кельтский крест", "Классический расклад из 10 карт", 10),
    ]
    
    for name, description, num_cards in spreads_data:
        spread, created = TarotSpread.objects.get_or_create(
            name=name,
            project=project,
            defaults={
                'description': description,
                'num_cards': num_cards
            }
        )
        print(f"Расклад: {spread.name} ({'создан' if created else 'уже существует'})")
    
    # 6. Создаем пакеты
    packages_data = [
        ("Базовый пакет", 100, "one_time", 5, None),
        ("Расширенный пакет", 200, "one_time", 15, None),
        ("Месячная подписка", 500, "subscription", None, 30),
        ("Годовая подписка", 5000, "subscription", None, 365),
    ]
    
    for name, price, pkg_type, num_readings, subscription_days in packages_data:
        package, created = Package.objects.get_or_create(
            name=name,
            project=project,
            defaults={
                'price': price,
                'package_type': pkg_type,
                'num_readings': num_readings,
                'subscription_days': subscription_days,
                'is_active': True
            }
        )
        print(f"Пакет: {package.name} ({'создан' if created else 'уже существует'})")
    
    # 7. Создаем тестовую интерпретацию
    if not Interpretation.objects.filter(user=user).exists():
        spread = TarotSpread.objects.filter(project=project).first()
        cards = TarotCard.objects.filter(deck=deck)[:3]
        
        interpretation = Interpretation.objects.create(
            user=user,
            spread=spread,
            ai_response="Это тестовая интерпретация. Карты показывают, что в вашей жизни наступает период изменений. Будьте открыты новым возможностям и доверяйте своей интуиции."
        )
        interpretation.cards.set(cards)
        print(f"Тестовая интерпретация создана")
    
    print("\n✅ Тестовые данные успешно созданы!")
    print(f"Проект ID: {project.id}")
    print(f"Пользователь ID: {user.id}")
    print(f"Колода ID: {deck.id}")

if __name__ == '__main__':
    create_test_data() 