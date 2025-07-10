import logging
from typing import Dict, Any
from django.utils import timezone
from datetime import timedelta

from projects.models import Project
from users.models import UserProfile
from tarot.models import TarotSpread, TarotCard, Interpretation
from payments.models import Package

logger = logging.getLogger(__name__)

class TelegramBotHandler:
    """Имитация обработчика Telegram Bot API"""
    
    def __init__(self, project: Project):
        self.project = project
        self.bot_token = project.telegram_token
        
    def handle_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка входящего сообщения"""
        message_type = message_data.get('type', 'text')
        
        if message_type == 'command':
            return self._handle_command(message_data)
        elif message_type == 'text':
            return self._handle_text(message_data)
        else:
            return self._create_response("Неизвестный тип сообщения")
    
    def _handle_command(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка команд"""
        command = message_data.get('command', '')
        user_id = message_data.get('user_id')
        username = message_data.get('username', '')
        
        # Получаем или создаем пользователя
        user, created = UserProfile.objects.get_or_create(
            project=self.project,
            telegram_user_id=user_id,
            defaults={'username': username}
        )
        
        if command == '/start':
            return self._handle_start(user)
        elif command == '/help':
            return self._handle_help(user)
        elif command == '/tarot':
            return self._handle_tarot(user)
        elif command == '/balance':
            return self._handle_balance(user)
        elif command == '/packages':
            return self._handle_packages(user)
        else:
            return self._create_response("Неизвестная команда. Используйте /help для справки.")
    
    def _handle_start(self, user: UserProfile) -> Dict[str, Any]:
        """Обработка команды /start"""
        welcome_text = f"""
🔮 Добро пожаловать в {self.project.name}!

Я помогу вам получить предсказание с помощью карт Таро.

Доступные команды:
/tarot - Получить предсказание
/balance - Проверить баланс
/packages - Доступные пакеты
/help - Помощь

Ваш баланс: {user.balance} раскладов
        """
        return self._create_response(welcome_text.strip())
    
    def _handle_help(self, user: UserProfile) -> Dict[str, Any]:
        """Обработка команды /help"""
        help_text = f"""
🔮 {self.project.name} - Помощь

Команды:
/start - Начать работу с ботом
/tarot - Получить предсказание (стоимость: 1 расклад)
/balance - Проверить баланс раскладов
/packages - Посмотреть доступные пакеты
/help - Показать эту справку

Для получения предсказания используйте команду /tarot
        """
        return self._create_response(help_text.strip())
    
    def _handle_tarot(self, user: UserProfile) -> Dict[str, Any]:
        """Обработка команды /tarot"""
        # Проверяем баланс
        if user.balance <= 0:
            return self._create_response(
                "❌ У вас закончились расклады!\n"
                "Используйте /packages для покупки новых раскладов."
            )
        
        # Получаем случайный расклад
        spreads = TarotSpread.objects.filter(project=self.project)
        if not spreads.exists():
            return self._create_response("❌ Нет доступных раскладов.")
        
        spread = spreads.first()
        
        # Получаем карты для расклада
        cards = TarotCard.objects.filter(deck__project=self.project).order_by('?')[:spread.num_cards]
        
        if len(cards) < spread.num_cards:
            return self._create_response("❌ Недостаточно карт для расклада.")
        
        # Создаем интерпретацию
        interpretation = Interpretation.objects.create(
            user=user,
            spread=spread,
            ai_response="Это пример AI-интерпретации для вашего расклада. В реальной версии здесь будет ответ от OpenAI."
        )
        interpretation.cards.set(cards)
        
        # Уменьшаем баланс
        user.balance -= 1
        user.save()
        
        # Формируем ответ
        cards_text = "\n".join([f"• {card.name}" for card in cards])
        response_text = f"""
🔮 Ваше предсказание:

Расклад: {spread.name}
Карты: {cards_text}

Интерпретация:
{interpretation.ai_response}

Осталось раскладов: {user.balance}
        """
        return self._create_response(response_text.strip())
    
    def _handle_balance(self, user: UserProfile) -> Dict[str, Any]:
        """Обработка команды /balance"""
        balance_text = f"""
💰 Ваш баланс:

Раскладов: {user.balance}
        """
        
        if user.subscription_start and user.subscription_end:
            if timezone.now().date() <= user.subscription_end:
                balance_text += f"\nПодписка активна до: {user.subscription_end.strftime('%d.%m.%Y')}"
            else:
                balance_text += "\nПодписка истекла"
        
        return self._create_response(balance_text.strip())
    
    def _handle_packages(self, user: UserProfile) -> Dict[str, Any]:
        """Обработка команды /packages"""
        packages = Package.objects.filter(project=self.project, is_active=True)
        
        if not packages.exists():
            return self._create_response("❌ Нет доступных пакетов.")
        
        packages_text = "📦 Доступные пакеты:\n\n"
        
        for package in packages:
            if package.package_type == 'one_time':
                packages_text += f"• {package.name} - {package.price}₽ ({package.num_readings} раскладов)\n"
            else:
                packages_text += f"• {package.name} - {package.price}₽ ({package.subscription_days} дней подписки)\n"
        
        packages_text += "\nДля покупки обратитесь к администратору."
        
        return self._create_response(packages_text.strip())
    
    def _handle_text(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка текстовых сообщений"""
        return self._create_response("Используйте команды для взаимодействия с ботом. /help для справки.")
    
    def _create_response(self, text: str) -> Dict[str, Any]:
        """Создание ответа"""
        return {
            'type': 'text',
            'text': text,
            'timestamp': timezone.now().isoformat(),
            'bot_token': self.bot_token
        }

class TelegramBotManager:
    """Менеджер для управления несколькими ботами"""
    
    @staticmethod
    def get_bot_handler(project_id: int) -> TelegramBotHandler:
        """Получение обработчика для конкретного проекта"""
        try:
            project = Project.objects.get(id=project_id, status='active')
            return TelegramBotHandler(project)
        except Project.DoesNotExist:
            raise ValueError(f"Проект {project_id} не найден или неактивен")
    
    @staticmethod
    def handle_webhook(project_id: int, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка webhook от Telegram"""
        handler = TelegramBotManager.get_bot_handler(project_id)
        return handler.handle_message(message_data)
    
    @staticmethod
    def get_active_bots() -> list:
        """Получение списка активных ботов"""
        return Project.objects.filter(status='active') 