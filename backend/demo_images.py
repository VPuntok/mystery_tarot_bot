#!/usr/bin/env python
"""
Демонстрационный скрипт для работы с изображениями карт Таро
"""
import os
import django
from pathlib import Path

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from tarot.models import TarotCard

def demo_images():
    """Демонстрация работы с изображениями"""
    print("🎴 Демонстрация работы с изображениями карт Таро")
    print("=" * 50)
    
    # Показываем несколько карт
    cards = TarotCard.objects.all()[:5]
    
    print(f"\n📋 Примеры карт в базе данных:")
    for card in cards:
        image_status = "✅" if card.image else "❌"
        print(f"  {image_status} {card.name} - {card.image or 'без изображения'}")
    
    print(f"\n📁 Папки для изображений:")
    print(f"  Статические: {Path('static/tarot/cards').absolute()}")
    print(f"  Медиа: {Path('media/tarot/cards').absolute()}")
    
    print(f"\n💡 Как добавить изображения:")
    print("1. Поместите изображения в папку static/tarot/cards/")
    print("2. Имена файлов должны соответствовать названиям карт")
    print("3. Запустите: python link_card_images.py")
    print("4. Проверьте результат: python update_card_images.py")
    
    print(f"\n🌐 URL для доступа к изображениям:")
    print("  http://localhost:8000/static/tarot/cards/Шут.jpg")
    print("  http://localhost:8000/static/tarot/cards/Маг.png")
    
    print(f"\n📖 Подробная документация: IMAGES_README.md")

if __name__ == '__main__':
    demo_images() 