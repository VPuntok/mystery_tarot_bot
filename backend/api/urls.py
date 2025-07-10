from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProjectViewSet, UserProfileViewSet, TarotDeckViewSet, TarotCardViewSet,
    TarotSpreadViewSet, InterpretationViewSet, PackageViewSet, PaymentViewSet,
    TelegramBotViewSet, HealthCheckView
)

router = DefaultRouter()
router.register(r'projects', ProjectViewSet)
router.register(r'users', UserProfileViewSet)
router.register(r'tarot/decks', TarotDeckViewSet)
router.register(r'tarot/cards', TarotCardViewSet)
router.register(r'tarot/spreads', TarotSpreadViewSet)
router.register(r'tarot/interpretations', InterpretationViewSet)
router.register(r'packages', PackageViewSet)
router.register(r'payments', PaymentViewSet)
router.register(r'telegram', TelegramBotViewSet, basename='telegram')

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health-check'),
    path('', include(router.urls)),
] 