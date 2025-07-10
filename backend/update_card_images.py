#!/usr/bin/env python
"""
Скрипт для обновления карт Таро с изображениями
"""
import os
import django
from pathlib import Path

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from tarot.models import TarotCard

def update_card_images():
    """Обновление карт с изображениями"""
    print("Обновление карт с изображениями...")
    
    # Путь к папке с изображениями
    images_dir = Path("static/tarot/cards")
    media_dir = Path("media/tarot/cards")
    
    # Создаем папки, если их нет
    images_dir.mkdir(parents=True, exist_ok=True)
    media_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📁 Папка для статических изображений: {images_dir.absolute()}")
    print(f"📁 Папка для медиа изображений: {media_dir.absolute()}")
    
    # Получаем все карты
    cards = TarotCard.objects.all()
    
    print(f"\n🎴 Найдено карт в базе: {cards.count()}")
    
    # Проверяем, какие изображения есть
    image_files = list(images_dir.glob("*.jpg")) + list(images_dir.glob("*.png")) + list(images_dir.glob("*.jpeg"))
    media_files = list(media_dir.glob("*.jpg")) + list(media_dir.glob("*.png")) + list(media_dir.glob("*.jpeg"))
    
    print(f"📸 Найдено изображений в static: {len(image_files)}")
    print(f"📸 Найдено изображений в media: {len(media_files)}")
    
    if image_files:
        print("\n📋 Список изображений в static/tarot/cards/:")
        for img in image_files:
            print(f"  - {img.name}")
    
    if media_files:
        print("\n📋 Список изображений в media/tarot/cards/:")
        for img in media_files:
            print(f"  - {img.name}")
    
    print("\n💡 Инструкции:")
    print("1. Поместите изображения карт в папку static/tarot/cards/")
    print("2. Имена файлов должны соответствовать названиям карт")
    print("3. Поддерживаемые форматы: .jpg, .png, .jpeg")
    print("4. Примеры имен файлов:")
    print("   - Шут.jpg")
    print("   - Маг.png")
    print("   - Туз Кубков.jpg")
    print("   - Двойка Мечей.png")
    
    # Показываем карты без изображений
    cards_without_images = [card for card in cards if not card.image]
    if cards_without_images:
        print(f"\n❌ Карты без изображений ({len(cards_without_images)}):")
        for card in cards_without_images[:10]:  # Показываем первые 10
            print(f"  - {card.name}")
        if len(cards_without_images) > 10:
            print(f"  ... и еще {len(cards_without_images) - 10} карт")
    
    # Показываем карты с изображениями
    cards_with_images = [card for card in cards if card.image]
    if cards_with_images:
        print(f"\n✅ Карты с изображениями ({len(cards_with_images)}):")
        for card in cards_with_images[:5]:  # Показываем первые 5
            print(f"  - {card.name}: {card.image}")
        if len(cards_with_images) > 5:
            print(f"  ... и еще {len(cards_with_images) - 5} карт")

if __name__ == '__main__':
    update_card_images() 