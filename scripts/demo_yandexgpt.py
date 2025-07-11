#!/usr/bin/env python
"""
Демонстрационный скрипт для работы с YandexGPT Lite
"""
import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from tarot.services import yandex_gpt_service
from tarot.models import TarotSpread, TarotCard, Interpretation
from projects.models import Project
from users.models import UserProfile

def demo_yandexgpt():
    """Демонстрация работы с YandexGPT"""
    print("🔮 Демонстрация YandexGPT Lite для интерпретации Таро")
    print("=" * 60)
    
    # Проверяем подключение
    print("1. Проверка подключения к YandexGPT...")
    if yandex_gpt_service.test_connection():
        print("✅ YandexGPT доступен и работает!")
    else:
        print("⚠️ YandexGPT недоступен, используются запасные интерпретации")
    
    print("\n2. Тестирование с тестовыми картами...")
    
    # Тестовые карты
    test_cards = [
        {'name': 'Шут', 'meaning': 'Новые начинания, спонтанность, свобода'},
        {'name': 'Маг', 'meaning': 'Сила воли, проявление, ресурсы'},
        {'name': 'Верховная жрица', 'meaning': 'Интуиция, тайные знания, подсознание'},
        {'name': 'Императрица', 'meaning': 'Плодородие, материнство, творчество'},
        {'name': 'Император', 'meaning': 'Власть, стабильность, авторитет'}
    ]
    
    # Генерируем интерпретацию
    interpretation = yandex_gpt_service.generate_interpretation(
        spread_name="Кельтский крест",
        cards=test_cards,
        user_context="Вопрос о карьерном росте и новых возможностях"
    )
    
    print("📝 Сгенерированная интерпретация:")
    print("-" * 50)
    print(interpretation)
    print("-" * 50)
    
    print("\n3. Тестирование с реальными данными из БД...")
    
    try:
        # Получаем тестовый проект
        project = Project.objects.first()
        if project:
            spread = TarotSpread.objects.filter(project=project).first()
            cards = TarotCard.objects.filter(deck__project=project)[:3]
            
            if spread and cards.exists():
                cards_data = []
                for card in cards:
                    cards_data.append({
                        'name': card.name,
                        'meaning': card.meaning_upright,
                        'reversed': False
                    })
                
                print(f"📊 Используем расклад: {spread.name}")
                print(f"📋 Карты: {', '.join([card['name'] for card in cards_data])}")
                
                # Генерируем интерпретацию
                db_interpretation = yandex_gpt_service.generate_interpretation(
                    spread_name=spread.name,
                    cards=cards_data,
                    user_context="Тестовый запрос из базы данных"
                )
                
                print("\n📝 Интерпретация из БД:")
                print("-" * 50)
                print(db_interpretation)
                print("-" * 50)
            else:
                print("❌ Не найдены расклады или карты в БД")
        else:
            print("❌ Не найдены проекты в БД")
            
    except Exception as e:
        print(f"❌ Ошибка при работе с БД: {e}")
    
    print("\n4. Создание интерпретации в БД...")
    
    try:
        user = UserProfile.objects.first()
        if user and spread and cards.exists():
            # Создаем интерпретацию в БД
            interpretation_obj = Interpretation.objects.create(
                user=user,
                spread=spread,
                ai_response=db_interpretation
            )
            interpretation_obj.cards.set(cards)
            
            print(f"✅ Интерпретация создана в БД с ID: {interpretation_obj.id}")
            print(f"👤 Пользователь: {user.username}")
            print(f"🔮 Расклад: {spread.name}")
            print(f"📅 Дата: {interpretation_obj.created_at}")
        else:
            print("❌ Не удалось создать интерпретацию в БД")
            
    except Exception as e:
        print(f"❌ Ошибка при создании интерпретации: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Демонстрация завершена!")
    print("\n💡 Для настройки YandexGPT:")
    print("1. Получите API ключ в Yandex Cloud Console")
    print("2. Добавьте YANDEX_API_KEY и YANDEX_FOLDER_ID в .env")
    print("3. Перезапустите приложение")
    print("\n📚 Подробнее: backend/YANDEXGPT_SETUP.md")

if __name__ == "__main__":
    demo_yandexgpt() 