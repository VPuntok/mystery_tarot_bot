#!/usr/bin/env python
"""
Скрипт для автоматического связывания изображений с картами Таро (англоязычные имена файлов)
"""
import os
import django
from pathlib import Path
import re

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from tarot.models import TarotCard

# Словарь соответствий для старших арканов
EN_RU_MAP = {
    "TheFool": "Шут",
    "TheMagician": "Маг",
    "TheHighPriestess": "Верховная Жрица",
    "TheEmpress": "Императрица",
    "TheEmperor": "Император",
    "TheHierophant": "Иерофант",
    "TheLovers": "Влюбленные",
    "TheChariot": "Колесница",
    "Strength": "Сила",
    "TheHermit": "Отшельник",
    "WheelOfFortune": "Колесо Фортуны",
    "Justice": "Справедливость",
    "TheHangedMan": "Повешенный",
    "Death": "Смерть",
    "Temperance": "Умеренность",
    "TheDevil": "Дьявол",
    "TheTower": "Башня",
    "TheStar": "Звезда",
    "TheMoon": "Луна",
    "TheSun": "Солнце",
    "Judgement": "Суд",
    "TheWorld": "Мир",
}

# Маппинг для младших арканов
SUITS_RU = {
    'Cups': 'Кубков',
    'Swords': 'Мечей',
    'Wands': 'Жезлов',
    'Pentacles': 'Пентаклей',
}
RANKS_RU = {
    '01': 'Туз',
    '02': 'Двойка',
    '03': 'Тройка',
    '04': 'Четверка',
    '05': 'Пятерка',
    '06': 'Шестерка',
    '07': 'Семерка',
    '08': 'Восьмерка',
    '09': 'Девятка',
    '10': 'Десятка',
    '11': 'Паж',
    '12': 'Рыцарь',
    '13': 'Королева',
    '14': 'Король',
}

def get_russian_name_from_filename(filename):
    # Старшие арканы
    match = re.match(r'\d{2}-(\w+)', filename)
    if match:
        en = match.group(1)
        return EN_RU_MAP.get(en)
    # Младшие арканы
    match = re.match(r'(Cups|Swords|Wands|Pentacles)(\d{2})', filename)
    if match:
        suit_en, rank_en = match.groups()
        rank_ru = RANKS_RU.get(rank_en)
        suit_ru = SUITS_RU.get(suit_en)
        if rank_ru and suit_ru:
            return f"{rank_ru} {suit_ru}"
    return None

def link_card_images():
    print("🔗 Связывание изображений с картами (media/tarot/cards)...")
    images_dir = Path("media/tarot/cards")
    if not images_dir.exists():
        print(f"❌ Папка {images_dir} не найдена!")
        return
    image_files = list(images_dir.glob("*.jpg")) + list(images_dir.glob("*.png")) + list(images_dir.glob("*.jpeg"))
    if not image_files:
        print(f"❌ В папке {images_dir} нет изображений!")
        return
    print(f"📸 Найдено изображений: {len(image_files)}")
    cards = TarotCard.objects.all()
    cards_dict = {card.name: card for card in cards}
    linked_count = 0
    not_found = []
    for img_file in image_files:
        name_without_ext = img_file.stem
        ru_name = get_russian_name_from_filename(name_without_ext)
        if ru_name and ru_name in cards_dict:
            card = cards_dict[ru_name]
            card.image = f"tarot/cards/{img_file.name}"
            card.save()
            print(f"✅ Связано: {ru_name} -> {img_file.name}")
            linked_count += 1
        else:
            not_found.append(img_file.name)
    print(f"\n📊 Связано карт: {linked_count}")
    if not_found:
        print(f"❌ Не удалось сопоставить: {len(not_found)} файлов")
        for n in not_found[:10]:
            print(f"  - {n}")
        if len(not_found) > 10:
            print(f"  ... и еще {len(not_found)-10} файлов")
    cards_without_images = [card for card in cards if not card.image]
    if cards_without_images:
        print(f"\n❌ Карты без изображений ({len(cards_without_images)}):")
        for card in cards_without_images[:10]:
            print(f"  - {card.name}")
        if len(cards_without_images) > 10:
            print(f"  ... и еще {len(cards_without_images) - 10} карт")
    print("\nГотово!")

if __name__ == '__main__':
    link_card_images() 