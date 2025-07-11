#!/usr/bin/env python
"""
Скрипт для добавления новых раскладов
"""
import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from projects.models import Project
from tarot.models import TarotSpread

def add_spreads():
    """Добавление новых раскладов"""
    print("Добавление новых раскладов...")
    
    # Получаем тестовый проект
    try:
        project = Project.objects.get(name="Mystic Tarot Bot")
    except Project.DoesNotExist:
        print("❌ Проект 'Mystic Tarot Bot' не найден!")
        return
    
    # Новые расклады
    new_spreads = [
        {
            "name": "Расклад любви",
            "description": "Гадание на любовь и отношения. 7 карт раскрывают прошлое, настоящее и будущее ваших чувств.",
            "num_cards": 7
        },
        {
            "name": "Расклад карьеры",
            "description": "Профессиональное гадание. 5 карт покажут ваш карьерный путь и возможности роста.",
            "num_cards": 5
        },
        {
            "name": "Расклад здоровья",
            "description": "Гадание на здоровье и благополучие. 4 карты раскроют состояние вашего здоровья.",
            "num_cards": 4
        },
        {
            "name": "Расклад денег",
            "description": "Финансовое гадание. 6 карт покажут ваше финансовое будущее и возможности.",
            "num_cards": 6
        },
        {
            "name": "Расклад путешествий",
            "description": "Гадание на путешествия и поездки. 3 карты предскажут ваши будущие путешествия.",
            "num_cards": 3
        },
        {
            "name": "Расклад семьи",
            "description": "Семейное гадание. 8 карт раскроют отношения в семье и семейные события.",
            "num_cards": 8
        },
        {
            "name": "Расклад дружбы",
            "description": "Гадание на дружбу и социальные связи. 4 карты покажут ваши отношения с друзьями.",
            "num_cards": 4
        },
        {
            "name": "Расклад духовного роста",
            "description": "Гадание на духовное развитие. 9 карт покажут ваш духовный путь и возможности роста.",
            "num_cards": 9
        },
        {
            "name": "Расклад принятия решений",
            "description": "Гадание для принятия важных решений. 5 карт помогут выбрать правильный путь.",
            "num_cards": 5
        },
        {
            "name": "Расклад прошлых жизней",
            "description": "Кармическое гадание. 6 карт раскроют тайны ваших прошлых воплощений.",
            "num_cards": 6
        }
    ]
    
    created_count = 0
    for spread_data in new_spreads:
        spread, created = TarotSpread.objects.get_or_create(
            name=spread_data["name"],
            project=project,
            defaults={
                'description': spread_data["description"],
                'num_cards': spread_data["num_cards"]
            }
        )
        
        if created:
            print(f"✅ Создан расклад: {spread.name} ({spread.num_cards} карт)")
            created_count += 1
        else:
            print(f"⏭️  Расклад уже существует: {spread.name}")
    
    print(f"\n🎯 Итого создано новых раскладов: {created_count}")
    
    # Показываем общее количество раскладов
    total_spreads = TarotSpread.objects.filter(project=project).count()
    print(f"📊 Всего раскладов в проекте: {total_spreads}")

if __name__ == '__main__':
    add_spreads() 