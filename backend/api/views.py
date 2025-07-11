from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone

from .serializers import (
    ProjectSerializer, UserProfileSerializer, TarotDeckSerializer, TarotCardSerializer,
    TarotSpreadSerializer, InterpretationSerializer, PackageSerializer, 
    PaymentSerializer, PaymentCreateSerializer, ThemeSettingsSerializer
)
from projects.models import Project
from users.models import UserProfile
from tarot.models import TarotDeck, TarotCard, TarotSpread, Interpretation
from payments.models import Package, Payment
from telegram_bot.handlers import TelegramBotManager
from tarot.services import yandex_gpt_service

class HealthCheckView(APIView):
    """Простой endpoint для проверки здоровья API"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        # Проверяем статус YandexGPT сервиса
        yandex_status = yandex_gpt_service.get_model_info()
        
        return Response({
            'status': 'ok',
            'message': 'API работает корректно',
            'timestamp': timezone.now().isoformat(),
            'yandexgpt': {
                'sdk_available': yandex_status['sdk_available'],
                'model_initialized': yandex_status['model_initialized'],
                'api_key_configured': yandex_status['api_key_configured'],
                'folder_id_configured': yandex_status['folder_id_configured'],
                'connection_test': yandex_status['connection_test']
            }
        })

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [AllowAny]  # Временно отключаем аутентификацию для тестирования
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['name']
    ordering_fields = ['created_at', 'name']

    @action(detail=True, methods=['get'])
    def theme_settings(self, request, pk=None):
        """Получение настроек темы для проекта"""
        project = self.get_object()
        serializer = self.get_serializer(project)
        return Response({
            'success': True,
            'theme_settings': serializer.data['theme_settings']
        })

    @action(detail=True, methods=['post'])
    def update_theme_settings(self, request, pk=None):
        """Обновление настроек темы для проекта"""
        project = self.get_object()
        theme_serializer = ThemeSettingsSerializer(data=request.data)
        
        if theme_serializer.is_valid():
            # Обновляем поле design с новыми настройками темы
            current_design = project.design or {}
            current_design.update(theme_serializer.validated_data)
            project.design = current_design
            project.save()
            
            # Возвращаем обновленные настройки
            serializer = self.get_serializer(project)
            return Response({
                'success': True,
                'message': 'Настройки темы обновлены',
                'theme_settings': serializer.data['theme_settings']
            })
        else:
            return Response({
                'success': False,
                'errors': theme_serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """Имитация отправки сообщения боту"""
        project = self.get_object()
        
        try:
            handler = TelegramBotManager.get_bot_handler(project.id)
            response = handler.handle_message(request.data)
            return Response(response)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [AllowAny]  # Временно отключаем аутентификацию для тестирования
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['project', 'balance']
    search_fields = ['username', 'telegram_user_id']
    ordering_fields = ['created_at', 'username']

class TarotDeckViewSet(viewsets.ModelViewSet):
    queryset = TarotDeck.objects.all()
    serializer_class = TarotDeckSerializer
    permission_classes = [AllowAny]  # Временно отключаем аутентификацию для тестирования
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['project']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'name']

class TarotCardViewSet(viewsets.ModelViewSet):
    queryset = TarotCard.objects.all()
    serializer_class = TarotCardSerializer
    permission_classes = [AllowAny]  # Временно отключаем аутентификацию для тестирования
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['deck']
    search_fields = ['name', 'meaning_upright', 'meaning_reversed']
    ordering_fields = ['order', 'name']

class TarotSpreadViewSet(viewsets.ModelViewSet):
    queryset = TarotSpread.objects.all()
    serializer_class = TarotSpreadSerializer
    permission_classes = [AllowAny]  # Временно отключаем аутентификацию для тестирования
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['project', 'num_cards']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'name']

class InterpretationViewSet(viewsets.ModelViewSet):
    queryset = Interpretation.objects.all()
    serializer_class = InterpretationSerializer
    permission_classes = [AllowAny]  # Временно отключаем аутентификацию для тестирования
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['user', 'spread']
    search_fields = ['ai_response']
    ordering_fields = ['created_at']

    @action(detail=False, methods=['post'])
    def create_interpretation(self, request):
        """Создание новой интерпретации с AI-ответом"""
        try:
            # Получаем данные
            user_id = request.data.get('user')
            spread_id = request.data.get('spread')
            interpretation_id = request.data.get('interpretation_id')  # ID существующей интерпретации
            user_context = request.data.get('user_context', '')  # Дополнительный контекст от пользователя
            
            if not user_id or not spread_id:
                return Response({
                    'error': 'Необходимы поля user и spread'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Получаем объекты
            user = UserProfile.objects.get(id=user_id)
            spread = TarotSpread.objects.get(id=spread_id)
            
            # Если указан interpretation_id, используем существующую интерпретацию
            if interpretation_id:
                try:
                    interpretation = Interpretation.objects.get(id=interpretation_id, user=user, spread=spread)
                    cards = list(interpretation.cards.all())
                except Interpretation.DoesNotExist:
                    return Response({
                        'error': 'Интерпретация не найдена'
                    }, status=status.HTTP_404_NOT_FOUND)
            else:
                # Проверяем баланс пользователя (только для новых интерпретаций)
                if user.balance <= 0:
                    return Response({
                        'error': 'Недостаточно раскладов. Пополните баланс.'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Получаем карты для расклада
                cards = TarotCard.objects.filter(deck__project=spread.project).order_by('?')[:spread.num_cards]
                
                if len(cards) < spread.num_cards:
                    return Response({
                        'error': f'Недостаточно карт для расклада. Нужно {spread.num_cards}, доступно {len(cards)}'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Создаем новую интерпретацию
                interpretation = Interpretation.objects.create(
                    user=user,
                    spread=spread,
                    ai_response='',
                    user_question=user_context if user_context else None
                )
                interpretation.cards.set(cards)
                
                # Уменьшаем баланс пользователя
                user.balance -= 1
                user.save()
            
            # Подготавливаем данные карт для AI
            cards_data = []
            for card in cards:
                # Определяем, прямая или перевернутая карта (случайно)
                import random
                is_reversed = random.choice([True, False])
                
                cards_data.append({
                    'name': card.name,
                    'meaning': card.meaning_reversed if is_reversed else card.meaning_upright,
                    'is_reversed': is_reversed
                })
            
            # Генерируем AI-ответ через сервис YandexGPT
            ai_response = yandex_gpt_service.generate_interpretation(
                spread_name=spread.name,
                cards=cards_data,
                user_context=user_context
            )
            
            # Обновляем интерпретацию с AI-ответом
            interpretation.ai_response = ai_response
            interpretation.save()
            
            # Возвращаем результат через сериализатор для правильной структуры
            serializer = self.get_serializer(interpretation, context={'request': request})
            response_data = serializer.data
            
            # Добавляем дополнительную информацию
            response_data['success'] = True
            response_data['cards_used'] = [{'name': card.name, 'is_reversed': card_data['is_reversed']} 
                                          for card, card_data in zip(cards, cards_data)]
            response_data['ai_service_status'] = 'active' if yandex_gpt_service.model else 'fallback'
            
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except UserProfile.DoesNotExist:
            return Response({
                'error': 'Пользователь не найден'
            }, status=status.HTTP_404_NOT_FOUND)
        except TarotSpread.DoesNotExist:
            return Response({
                'error': 'Расклад не найден'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': f'Ошибка создания интерпретации: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def get_cards(self, request):
        """Получение карт для расклада без создания интерпретации"""
        try:
            # Получаем данные
            user_id = request.data.get('user')
            spread_id = request.data.get('spread')
            user_context = request.data.get('user_context', '')  # Дополнительный контекст от пользователя
            
            if not user_id or not spread_id:
                return Response({
                    'error': 'Необходимы поля user и spread'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Получаем объекты
            user = UserProfile.objects.get(id=user_id)
            spread = TarotSpread.objects.get(id=spread_id)
            
            # Проверяем баланс пользователя
            if user.balance <= 0:
                return Response({
                    'error': 'Недостаточно раскладов. Пополните баланс.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Получаем карты для расклада
            cards = TarotCard.objects.filter(deck__project=spread.project).order_by('?')[:spread.num_cards]
            
            if len(cards) < spread.num_cards:
                return Response({
                    'error': f'Недостаточно карт для расклада. Нужно {spread.num_cards}, доступно {len(cards)}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Подготавливаем данные карт
            cards_data = []
            cards_names = []
            cards_images = []
            cards_used = []
            
            for card in cards:
                # Определяем, прямая или перевернутая карта (случайно)
                import random
                is_reversed = random.choice([True, False])
                
                cards_data.append({
                    'name': card.name,
                    'meaning': card.meaning_reversed if is_reversed else card.meaning_upright,
                    'is_reversed': is_reversed
                })
                
                cards_names.append(card.name)
                
                # Добавляем изображение карты
                request = self.request
                if card.image:
                    if request is not None:
                        cards_images.append(request.build_absolute_uri(card.image.url))
                    else:
                        cards_images.append(card.image.url)
                else:
                    cards_images.append('')
                
                cards_used.append({
                    'name': card.name,
                    'is_reversed': is_reversed
                })
            
            # Создаем временную интерпретацию (без AI-ответа) для связи карт
            interpretation = Interpretation.objects.create(
                user=user,
                spread=spread,
                ai_response='',  # Пустой ответ, будет заполнен позже
                user_question=user_context if user_context else None
            )
            interpretation.cards.set(cards)
            
            # Уменьшаем баланс пользователя
            user.balance -= 1
            user.save()
            
            # Возвращаем результат
            return Response({
                'success': True,
                'interpretation_id': interpretation.id,
                'spread_name': spread.name,
                'cards_names': cards_names,
                'cards_images': cards_images,
                'cards_used': cards_used,
                'new_balance': user.balance
            }, status=status.HTTP_200_OK)
            
        except UserProfile.DoesNotExist:
            return Response({
                'error': 'Пользователь не найден'
            }, status=status.HTTP_404_NOT_FOUND)
        except TarotSpread.DoesNotExist:
            return Response({
                'error': 'Расклад не найден'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': f'Ошибка получения карт: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PackageViewSet(viewsets.ModelViewSet):
    queryset = Package.objects.filter(is_active=True)
    serializer_class = PackageSerializer
    permission_classes = [AllowAny]  # Временно отключаем аутентификацию для тестирования
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['project', 'package_type', 'is_active']
    search_fields = ['name']
    ordering_fields = ['price', 'created_at', 'name']

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [AllowAny]  # Временно отключаем аутентификацию для тестирования
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['user', 'project', 'package', 'status']
    search_fields = ['external_id']
    ordering_fields = ['created_at', 'amount']

    def get_serializer_class(self):
        if self.action == 'create':
            return PaymentCreateSerializer
        return PaymentSerializer

    @action(detail=False, methods=['post'])
    def test_payment(self, request):
        """Тестовый платеж с PIN-кодом"""
        try:
            # Получаем данные
            user_id = request.data.get('user')
            project_id = request.data.get('project')
            package_id = request.data.get('package')
            pin_code = request.data.get('pin_code')
            
            if not all([user_id, project_id, package_id]):
                return Response({
                    'error': 'Необходимы поля: user, project, package'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Проверяем PIN-код
            if pin_code != '8712':
                return Response({
                    'error': 'Неверный PIN-код. Для тестирования используйте: 8712'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Получаем объекты
            user = UserProfile.objects.get(id=user_id)
            project = Project.objects.get(id=project_id)
            package = Package.objects.get(id=package_id)
            
            # Проверяем, что пакет активен
            if not package.is_active:
                return Response({
                    'error': 'Пакет неактивен'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Создаем платеж
            payment = Payment.objects.create(
                user=user,
                project=project,
                package=package,
                amount=package.price,
                status='completed',  # Сразу отмечаем как завершенный
                external_id=f'test_payment_{timezone.now().timestamp()}',
                payment_url='https://test-payment.example.com'
            )
            
            # Обновляем баланс пользователя
            if package.package_type == 'one_time':
                # Разовый пакет - добавляем расклады
                user.balance += package.num_readings
            else:
                # Подписка - устанавливаем даты подписки
                from datetime import timedelta
                user.subscription_start = timezone.now().date()
                user.subscription_end = timezone.now().date() + timedelta(days=package.subscription_days)
            
            user.save()
            
            # Возвращаем результат
            serializer = PaymentSerializer(payment)
            return Response({
                'success': True,
                'message': 'Тестовый платеж успешно выполнен!',
                'payment': serializer.data,
                'new_balance': user.balance,
                'subscription_end': user.subscription_end
            }, status=status.HTTP_201_CREATED)
            
        except UserProfile.DoesNotExist:
            return Response({
                'error': 'Пользователь не найден'
            }, status=status.HTTP_404_NOT_FOUND)
        except Project.DoesNotExist:
            return Response({
                'error': 'Проект не найден'
            }, status=status.HTTP_404_NOT_FOUND)
        except Package.DoesNotExist:
            return Response({
                'error': 'Пакет не найден'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': f'Ошибка создания тестового платежа: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def mark_completed(self, request, pk=None):
        """Отметить платеж как завершенный"""
        payment = self.get_object()
        payment.mark_as_completed()
        serializer = self.get_serializer(payment)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def mark_failed(self, request, pk=None):
        """Отметить платеж как неудачный"""
        payment = self.get_object()
        payment.mark_as_failed()
        serializer = self.get_serializer(payment)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def mark_cancelled(self, request, pk=None):
        """Отметить платеж как отмененный"""
        payment = self.get_object()
        payment.mark_as_cancelled()
        serializer = self.get_serializer(payment)
        return Response(serializer.data)

class TelegramBotViewSet(viewsets.ViewSet):
    """ViewSet для имитации Telegram Bot API"""
    permission_classes = [AllowAny]  # Временно отключаем аутентификацию для тестирования

    @action(detail=False, methods=['post'])
    def webhook(self, request):
        """Имитация webhook от Telegram"""
        project_id = request.data.get('project_id')
        message_data = request.data.get('message', {})
        
        try:
            response = TelegramBotManager.handle_webhook(project_id, message_data)
            return Response(response)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def active_bots(self, request):
        """Получение списка активных ботов"""
        bots = TelegramBotManager.get_active_bots()
        serializer = ProjectSerializer(bots, many=True)
        return Response(serializer.data)
