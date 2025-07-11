#!/usr/bin/env python
"""
Скрипт для добавления карт в колоду Таро
"""
import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from projects.models import Project
from tarot.models import TarotDeck, TarotCard

def add_cards():
    """Добавление карт в колоду"""
    print("Добавление карт в колоду...")
    
    # Получаем тестовый проект и колоду
    try:
        project = Project.objects.get(name="Mystic Tarot Bot")
        deck = TarotDeck.objects.get(name="Классическая колода Таро", project=project)
    except (Project.DoesNotExist, TarotDeck.DoesNotExist):
        print("❌ Проект или колода не найдены!")
        return
    
    # Дополнительные карты Таро (Старшие Арканы)
    additional_cards = [
        ("Колесо Фортуны", "Изменения, судьба, поворот событий", "Неудача, застой, плохие перемены"),
        ("Справедливость", "Баланс, справедливость, правда", "Несправедливость, дисбаланс, предвзятость"),
        ("Повешенный", "Жертва, пауза, новый взгляд", "Бесполезная жертва, застой, сопротивление"),
        ("Смерть", "Конец, трансформация, новое начало", "Страх перемен, застой, сопротивление"),
        ("Умеренность", "Баланс, гармония, терпение", "Дисбаланс, нетерпение, крайности"),
        ("Дьявол", "Искушение, материализм, зависимость", "Освобождение, преодоление искушений"),
        ("Башня", "Внезапные изменения, разрушение, откровение", "Избежание катастрофы, постепенные изменения"),
        ("Звезда", "Надежда, вдохновение, духовность", "Отчаяние, потеря веры, пессимизм"),
        ("Луна", "Интуиция, иллюзии, подсознание", "Ясность, преодоление страхов, правда"),
        ("Солнце", "Радость, успех, жизненная сила", "Временная депрессия, недостаток энергии"),
        ("Суд", "Возрождение, призыв, трансформация", "Сомнения, страх перемен, отказ от призыва"),
        ("Мир", "Завершение, гармония, путешествие", "Незавершенность, дисгармония, застой"),
    ]
    
    # Младшие Арканы - Масти
    suits = ["Кубки", "Мечи", "Пентакли", "Жезлы"]
    
    # Карты масти Кубки (Чувства, эмоции)
    cups_cards = [
        ("Туз Кубков", "Новые чувства, любовь, вдохновение", "Эмоциональная пустота, потеря вдохновения"),
        ("Двойка Кубков", "Партнерство, гармония, взаимность", "Разлад, непонимание, разрыв"),
        ("Тройка Кубков", "Празднование, дружба, радость", "Одиночество, изоляция, грусть"),
        ("Четверка Кубков", "Апатия, скука, неудовлетворенность", "Новые возможности, пробуждение"),
        ("Пятерка Кубков", "Разочарование, потеря, горе", "Принятие, исцеление, надежда"),
        ("Шестерка Кубков", "Ностальгия, детские воспоминания", "Застревание в прошлом, незрелость"),
        ("Семерка Кубков", "Выбор, иллюзии, мечты", "Ясность, принятие решений"),
        ("Восьмерка Кубков", "Уход, поиск, духовный путь", "Страх перемен, застой"),
        ("Девятка Кубков", "Удовлетворение, материальное благополучие", "Неудовлетворенность, жадность"),
        ("Десятка Кубков", "Семейное счастье, гармония, любовь", "Семейные проблемы, дисгармония"),
    ]
    
    # Карты масти Мечи (Интеллект, конфликты)
    swords_cards = [
        ("Туз Мечей", "Победа, сила, ясность мысли", "Поражение, слабость, путаница"),
        ("Двойка Мечей", "Выбор, равновесие, дилемма", "Нерешительность, страх выбора"),
        ("Тройка Мечей", "Сердечная боль, предательство, горе", "Исцеление, прощение, восстановление"),
        ("Четверка Мечей", "Отдых, восстановление, медитация", "Беспокойство, стресс, переутомление"),
        ("Пятерка Мечей", "Конфликт, поражение, унижение", "Примирение, прощение, мир"),
        ("Шестерка Мечей", "Переход, путешествие, исцеление", "Застревание, сопротивление переменам"),
        ("Семерка Мечей", "Хитрость, обман, скрытность", "Честность, открытость, прямота"),
        ("Восьмерка Мечей", "Ограничения, ловушка, беспомощность", "Освобождение, преодоление препятствий"),
        ("Девятка Мечей", "Тревога, страх, кошмары", "Надежда, облегчение, спокойствие"),
        ("Десятка Мечей", "Конец, предательство, боль", "Новое начало, исцеление, надежда"),
    ]
    
    # Карты масти Пентакли (Материя, деньги)
    pentacles_cards = [
        ("Туз Пентаклей", "Новые возможности, богатство, успех", "Упущенные возможности, материальные потери"),
        ("Двойка Пентаклей", "Баланс, адаптация, гибкость", "Дисбаланс, стресс, перегрузка"),
        ("Тройка Пентаклей", "Сотрудничество, мастерство, обучение", "Недостаток навыков, изоляция"),
        ("Четверка Пентаклей", "Сохранение, безопасность, консерватизм", "Щедрость, открытость, риск"),
        ("Пятерка Пентаклей", "Бедность, нужда, изоляция", "Восстановление, помощь, надежда"),
        ("Шестерка Пентаклей", "Щедрость, помощь, поддержка", "Эгоизм, долги, зависимость"),
        ("Семерка Пентаклей", "Терпение, планирование, рост", "Нетерпение, поспешность, неудача"),
        ("Восьмерка Пентаклей", "Упорный труд, мастерство, развитие", "Лень, отсутствие прогресса"),
        ("Девятка Пентаклей", "Благополучие, роскошь, независимость", "Материализм, одиночество"),
        ("Десятка Пентаклей", "Семейное богатство, наследие, традиции", "Семейные проблемы, потеря"),
    ]
    
    # Карты масти Жезлы (Энергия, творчество)
    wands_cards = [
        ("Туз Жезлов", "Новые начинания, вдохновение, энергия", "Отсутствие мотивации, задержки"),
        ("Двойка Жезлов", "Планирование, выбор, будущее", "Страх, нерешительность, ограничения"),
        ("Тройка Жезлов", "Расширение, путешествие, торговля", "Задержки, разочарование"),
        ("Четверка Жезлов", "Празднование, гармония, дом", "Семейные проблемы, дисгармония"),
        ("Пятерка Жезлов", "Конкуренция, конфликт, вызов", "Сотрудничество, мир, избежание конфликтов"),
        ("Шестерка Жезлов", "Победа, успех, признание", "Гордость, высокомерие, падение"),
        ("Семерка Жезлов", "Защита, вызов, настойчивость", "Уязвимость, поражение, слабость"),
        ("Восьмерка Жезлов", "Быстрые изменения, движение, новости", "Задержки, медленные изменения"),
        ("Девятка Жезлов", "Сила, выносливость, защита", "Слабость, уязвимость, истощение"),
        ("Десятка Жезлов", "Бремя, ответственность, нагрузка", "Освобождение, делегирование"),
    ]
    
    # Объединяем все карты
    all_cards = additional_cards + cups_cards + swords_cards + pentacles_cards + wands_cards
    
    created_count = 0
    for i, (name, upright, reversed) in enumerate(all_cards, start=11):  # Начинаем с 11, так как уже есть 10 карт
        card, created = TarotCard.objects.get_or_create(
            name=name,
            deck=deck,
            defaults={
                'meaning_upright': upright,
                'meaning_reversed': reversed,
                'order': i
            }
        )
        
        if created:
            print(f"✅ Создана карта: {card.name}")
            created_count += 1
        else:
            print(f"⏭️  Карта уже существует: {card.name}")
    
    print(f"\n🎯 Итого создано новых карт: {created_count}")
    
    # Показываем общее количество карт
    total_cards = TarotCard.objects.filter(deck=deck).count()
    print(f"📊 Всего карт в колоде: {total_cards}")

if __name__ == '__main__':
    add_cards() 