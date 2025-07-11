#!/usr/bin/env python
"""
Скрипт для создания расклада "Карта дня"
"""
import os
import sys
import django

# Добавляем путь к проекту
backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/backend'
sys.path.append(backend_path)

# Настраиваем Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from tarot.models import TarotSpread
from projects.models import Project

def create_card_of_day_spread():
    """Создает расклад 'Карта дня' для всех проектов"""
    
    # Получаем все активные проекты
    projects = Project.objects.filter(status='active')
    
    if not projects.exists():
        print("❌ Нет активных проектов")
        return
    
    for project in projects:
        # Проверяем, есть ли уже расклад "Карта дня" для этого проекта
        existing_spread = TarotSpread.objects.filter(
            project=project,
            name__icontains='карта дня'
        ).first()
        
        if existing_spread:
            print(f"✅ Расклад 'Карта дня' уже существует для проекта '{project.name}' (ID: {existing_spread.id})")
            continue
        
        # Создаем новый расклад "Карта дня"
        spread = TarotSpread.objects.create(
            project=project,
            name='Карта дня',
            description='Ежедневное предсказание на основе одной карты. Помогает понять энергетику дня и получить совет на текущий период.',
            num_cards=1
        )
        
        print(f"✅ Создан расклад 'Карта дня' для проекта '{project.name}' (ID: {spread.id})")
    
    print("\n🎯 Готово! Расклад 'Карта дня' создан для всех активных проектов.")

if __name__ == '__main__':
    create_card_of_day_spread() 