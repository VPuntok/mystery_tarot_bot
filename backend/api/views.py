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
    PaymentSerializer, PaymentCreateSerializer
)
from projects.models import Project
from users.models import UserProfile
from tarot.models import TarotDeck, TarotCard, TarotSpread, Interpretation
from payments.models import Package, Payment
from telegram_bot.handlers import TelegramBotManager

class HealthCheckView(APIView):
    """Простой endpoint для проверки здоровья API"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        return Response({
            'status': 'ok',
            'message': 'API работает корректно',
            'timestamp': timezone.now().isoformat()
        })

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [AllowAny]  # Временно отключаем аутентификацию для тестирования
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['name']
    ordering_fields = ['created_at', 'name']

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
            
            # Генерируем AI-ответ
            cards_text = ", ".join([card.name for card in cards])
            ai_response = f"""🔮 Ваше предсказание по раскладу "{spread.name}"

Выбранные карты: {cards_text}

Интерпретация:
Карты показывают, что в вашей жизни наступает период изменений и новых возможностей. 
Будьте открыты новым идеям и доверяйте своей интуиции. 
Впереди вас ждут интересные события и важные решения.

Совет: Слушайте свое сердце и не бойтесь перемен. 
Время действовать настало!"""
            
            # Создаем интерпретацию
            interpretation = Interpretation.objects.create(
                user=user,
                spread=spread,
                ai_response=ai_response
            )
            interpretation.cards.set(cards)
            
            # Уменьшаем баланс пользователя
            user.balance -= 1
            user.save()
            
            # Возвращаем результат
            serializer = self.get_serializer(interpretation)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
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
