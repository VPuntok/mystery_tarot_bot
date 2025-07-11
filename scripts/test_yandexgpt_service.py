from django.core.management.base import BaseCommand
from tarot.services import yandex_gpt_service


class Command(BaseCommand):
    help = 'Тестирует сервис YandexGPT с использованием официального SDK'

    def handle(self, *args, **options):
        self.stdout.write("🔮 Тест сервиса YandexGPT")
        self.stdout.write("=" * 50)
        
        # Получаем информацию о модели
        model_info = yandex_gpt_service.get_model_info()
        
        self.stdout.write(f"SDK доступен: {'✅' if model_info['sdk_available'] else '❌'}")
        self.stdout.write(f"Модель инициализирована: {'✅' if model_info['model_initialized'] else '❌'}")
        self.stdout.write(f"API ключ настроен: {'✅' if model_info['api_key_configured'] else '❌'}")
        self.stdout.write(f"Folder ID настроен: {'✅' if model_info['folder_id_configured'] else '❌'}")
        
        if model_info['model_initialized']:
            # Тестируем подключение
            self.stdout.write("\n🔧 Тестируем подключение...")
            connection_ok = yandex_gpt_service.test_connection()
            self.stdout.write(f"Подключение: {'✅' if connection_ok else '❌'}")
            
            if connection_ok:
                # Тестируем генерацию интерпретации
                self.stdout.write("\n📝 Тестируем генерацию интерпретации...")
                
                test_cards = [
                    {
                        'name': 'Шут',
                        'meaning': 'Начало нового пути, невинность, спонтанность'
                    },
                    {
                        'name': 'Маг',
                        'meaning': 'Сила воли, мастерство, новые возможности'
                    },
                    {
                        'name': 'Императрица',
                        'meaning': 'Плодородие, изобилие, материнство'
                    }
                ]
                
                interpretation = yandex_gpt_service.generate_interpretation(
                    spread_name="Тестовый расклад",
                    cards=test_cards,
                    user_context="Хочу узнать о своем будущем"
                )
                
                self.stdout.write("\n📖 Сгенерированная интерпретация:")
                self.stdout.write("-" * 40)
                self.stdout.write(interpretation)
                self.stdout.write("-" * 40)
                self.stdout.write("🎉 Сервис работает корректно!")
            else:
                self.stdout.write("❌ Не удалось подключиться к YandexGPT")
        else:
            self.stdout.write("❌ Модель не инициализирована")
            
        self.stdout.write("\n" + "=" * 50) 