# Mystic Tarot Bot

Телеграм-бот для предсказаний с помощью карт Таро.

## Структура проекта

- `backend/` - Python бэкенд с телеграм-ботом
- `frontend/` - JavaScript фронтенд (опционально)
- `database/` - Файлы базы данных
- `tests/` - Тесты

## Установка и запуск

### Backend

#### 1. Подготовка виртуального окружения

Перейдите в папку backend:
```bash
cd backend
```

Создайте виртуальное окружение:
```bash
python3 -m venv venv
```

Активируйте виртуальное окружение:

**На macOS/Linux:**
```bash
source venv/bin/activate
```

**На Windows:**
```bash
venv\Scripts\activate
```

#### 2. Установка зависимостей

Обновите pip:
```bash
pip install --upgrade pip
```

Установите зависимости:
```bash
pip install -r requirements.txt
```

#### 3. Настройка конфигурации

Создайте файл `.env` в папке `backend/`:
```bash
# Конфигурация Telegram бота
TELEGRAM_TOKEN=your_telegram_bot_token_here

# База данных
DATABASE_URL=sqlite:///bot.db

# Режим отладки
DEBUG=True

# Дополнительные настройки
LOG_LEVEL=INFO
```

**Важно:** Замените `your_telegram_bot_token_here` на ваш реальный токен бота, полученный от @BotFather.

#### 4. Запуск бота

**Способ 1: Прямой запуск**
```bash
python app/main.py
```

**Способ 2: Через скрипт запуска**
```bash
python run_bot.py
```

**Способ 3: Через скрипт управления**
```bash
python manage.py run
```

### Управление проектом

Используйте скрипт `manage.py` для различных операций:

```bash
# Установка зависимостей
python manage.py install

# Запуск тестов
python manage.py test

# Проверка кода
python manage.py check

# Настройка базы данных
python manage.py setup-db

# Запуск бота
python manage.py run

# Полная настройка проекта
python manage.py all
```

### Frontend (опционально)

1. Перейдите в папку frontend:
```bash
cd frontend
```

2. Установите зависимости:
```bash
npm install
```

3. Запустите в режиме разработки:
```bash
npm run dev
```

## Команды бота

- `/start` - Начать работу с ботом
- `/tarot` - Получить предсказание
- `/help` - Показать справку

## Разработка

### Структура backend

```
backend/
├── app/
│   ├── main.py          # Основной файл приложения
│   ├── bot/
│   │   ├── handlers.py  # Обработчики команд
│   │   └── keyboards.py # Клавиатуры
│   ├── services/
│   │   ├── tarot_service.py # Логика таро
│   │   └── user_service.py  # Работа с пользователями
│   ├── models/
│   │   └── user.py      # Модели данных
│   └── utils/
│       └── helpers.py   # Вспомогательные функции
├── venv/                # Виртуальное окружение
├── requirements.txt     # Зависимости Python
├── config.py           # Конфигурация
├── .env               # Переменные окружения
├── run_bot.py         # Скрипт запуска
└── manage.py          # Скрипт управления
```

### Полезные команды

**Активация виртуального окружения:**
```bash
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

**Деактивация виртуального окружения:**
```bash
deactivate
```

**Проверка установленных пакетов:**
```bash
pip list
```

**Обновление зависимостей:**
```bash
pip install -r requirements.txt --upgrade
```

**Создание нового requirements.txt:**
```bash
pip freeze > requirements.txt
```

## Получение токена бота

1. Найдите @BotFather в Telegram
2. Отправьте команду `/newbot`
3. Следуйте инструкциям для создания бота
4. Скопируйте полученный токен в файл `.env`

## Устранение неполадок

### Ошибка "ModuleNotFoundError"
Убедитесь, что виртуальное окружение активировано и зависимости установлены:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Ошибка "TELEGRAM_TOKEN not found"
Проверьте, что файл `.env` создан и содержит правильный токен.

### Ошибка "Permission denied"
Сделайте скрипты исполняемыми:
```bash
chmod +x run_bot.py manage.py
```
