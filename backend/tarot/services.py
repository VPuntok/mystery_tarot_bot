import json
import logging
from typing import List, Dict, Any
from django.conf import settings
from django.core.cache import cache

# Импортируем официальный SDK
try:
    from yandex_cloud_ml_sdk import YCloudML
    YANDEX_SDK_AVAILABLE = True
except ImportError:
    YANDEX_SDK_AVAILABLE = False
    logging.warning("Yandex Cloud ML SDK не установлен")

logger = logging.getLogger(__name__)

class YandexGPTService:
    """Сервис для работы с YandexGPT Lite через официальный SDK"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'YANDEX_API_KEY', None)
        self.folder_id = getattr(settings, 'YANDEX_FOLDER_ID', None)
        self.sdk = None
        self.model = None
        
        if not self.api_key or not self.folder_id:
            logger.warning("YandexGPT не настроен: отсутствуют API_KEY или FOLDER_ID")
            return
            
        if not YANDEX_SDK_AVAILABLE:
            logger.warning("Yandex Cloud ML SDK не установлен")
            return
            
        try:
            # Инициализируем SDK
            self.sdk = YCloudML(folder_id=self.folder_id, auth=self.api_key)
            # Получаем модель
            self.model = self.sdk.models.completions('yandexgpt-lite')
            # Настраиваем параметры по умолчанию
            self.model = self.model.configure(
                temperature=0.7,
                max_tokens=1000
            )
            logger.info("YandexGPT SDK успешно инициализирован")
        except Exception as e:
            logger.error(f"Ошибка инициализации YandexGPT SDK: {e}")
            self.sdk = None
            self.model = None
    
    def generate_interpretation(self, spread_name: str, cards: List[Dict], user_context: str = "") -> str:
        """
        Генерирует интерпретацию расклада с помощью YandexGPT Lite
        
        Args:
            spread_name: Название расклада
            cards: Список карт с их значениями
            user_context: Дополнительный контекст от пользователя (опционально)
        
        Returns:
            Строка с интерпретацией
        """
        if not self.model:
            logger.warning("YandexGPT модель недоступна, используем fallback")
            return self._get_fallback_interpretation(spread_name, cards)
        
        try:
            # Формируем промпт для AI
            prompt = self._build_prompt(spread_name, cards, user_context)
            
            # Отправляем запрос к YandexGPT через SDK
            result = self.model.run(prompt)
            
            if result:
                # Получаем текст из первого альтернативного ответа
                for alternative in result:
                    if hasattr(alternative, 'text') and alternative.text:
                        return alternative.text.strip()
                
                logger.warning("Получен пустой ответ от YandexGPT")
                return self._get_fallback_interpretation(spread_name, cards)
            else:
                logger.error("Не удалось получить ответ от YandexGPT")
                return self._get_fallback_interpretation(spread_name, cards)
                
        except Exception as e:
            logger.error(f"Ошибка при генерации интерпретации: {e}")
            return self._get_fallback_interpretation(spread_name, cards)
    
    def _build_prompt(self, spread_name: str, cards: List[Dict], user_context: str) -> str:
        """Строит промпт для YandexGPT"""
        
        cards_text = "\n".join([
            f"• {card['name']} - {card['meaning']}"
            for card in cards
        ])
        
        prompt = f"""Ты опытный таролог с глубокими знаниями карт Таро.
Твоя задача — создать краткую, но ёмкую и таинственную интерпретацию расклада.

РАСКЛАД: {spread_name}

ВЫПАВШИЕ КАРТЫ:
{cards_text}

{f'КОНТЕКСТ ОТ ПОЛЬЗОВАТЕЛЯ: {user_context}' if user_context else ''}

Создай интерпретацию, которая включает:
1. Общий смысл расклада (добавь 1-2 предложения с позитивом)
2. Толкование каждой карты в контексте расклада
3. Практические советы и рекомендации

В ответах добавляй таинственности и загадочности. Давай максимально сжатые, но ёмкие ответы. Используй эмодзи для украшения текста. Пиши на русском языке."""

        return prompt
    
    def _get_fallback_interpretation(self, spread_name: str, cards: List[Dict]) -> str:
        """Возвращает запасную интерпретацию, если AI недоступен"""
        
        cards_text = ", ".join([card['name'] for card in cards])
        
        interpretations = [
            f"""🔮 Ваше предсказание по раскладу "{spread_name}"

Выбранные карты: {cards_text}

Интерпретация:
Карты показывают, что в вашей жизни наступает период изменений и новых возможностей. 
Будьте открыты новым идеям и доверяйте своей интуиции. 
Впереди вас ждут интересные события и важные решения.

Совет: Слушайте свое сердце и не бойтесь перемен. 
Время действовать настало! 🌟""",
            
            f"""✨ Магическое предсказание: "{spread_name}"

Карты: {cards_text}

Ваши карты раскрывают тайны будущего и показывают путь к успеху. 
Вселенная благоволит вам в этот период. 
Доверьтесь мудрости карт и следуйте знакам судьбы.

Рекомендация: Будьте внимательны к знакам и возможностям, 
которые появятся на вашем пути. 🌙""",
            
            f"""🌟 Толкование расклада "{spread_name}"

Выпавшие карты: {cards_text}

Карты Таро говорят о том, что вы находитесь на пороге важных изменений. 
Ваша интуиция сейчас особенно сильна - прислушивайтесь к ней. 
Впереди ждут новые возможности и интересные встречи.

Наставление: Верьте в себя и свои силы. 
Вселенная поддерживает ваши стремления! ✨"""
        ]
        
        import random
        return random.choice(interpretations)
    
    def test_connection(self) -> bool:
        """Тестирует подключение к YandexGPT"""
        if not self.model:
            return False
        
        try:
            test_prompt = "Привет! Это тестовое сообщение. Ответь одним словом: 'Работает'"
            result = self.model.run(test_prompt)
            
            if result:
                for alternative in result:
                    if hasattr(alternative, 'text') and alternative.text:
                        return "работает" in alternative.text.lower()
            
            return False
        except Exception as e:
            logger.error(f"Ошибка тестирования подключения: {e}")
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Возвращает информацию о модели и статусе подключения"""
        return {
            'sdk_available': YANDEX_SDK_AVAILABLE,
            'model_initialized': self.model is not None,
            'api_key_configured': bool(self.api_key),
            'folder_id_configured': bool(self.folder_id),
            'connection_test': self.test_connection() if self.model else False
        }


# Создаем глобальный экземпляр сервиса
yandex_gpt_service = YandexGPTService() 