from rest_framework import serializers
from projects.models import Project
from users.models import UserProfile
from tarot.models import TarotDeck, TarotCard, TarotSpread, Interpretation
from payments.models import Package, Payment

class ProjectSerializer(serializers.ModelSerializer):
    theme_settings = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = ['id', 'name', 'telegram_token', 'design', 'theme_settings', 'status', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
    
    def get_theme_settings(self, obj):
        """Получаем настройки темы из поля design или возвращаем дефолтные"""
        design = obj.design or {}
        return {
            'primary_color': design.get('primary_color', '#6366f1'),
            'secondary_color': design.get('secondary_color', '#8b5cf6'),
            'accent_color': design.get('accent_color', '#f59e0b'),
            'bg_primary': design.get('bg_primary', '#0f0f23'),
            'bg_secondary': design.get('bg_secondary', '#1a1a2e'),
            'bg_card': design.get('bg_card', '#1e293b'),
            'text_primary': design.get('text_primary', '#f8fafc'),
            'text_secondary': design.get('text_secondary', '#cbd5e1'),
            'text_muted': design.get('text_muted', '#64748b'),
            'border_color': design.get('border_color', '#334155'),
            'font_family': design.get('font_family', 'Inter'),
            'border_radius': design.get('border_radius', '12px'),
            'is_dark_theme': design.get('is_dark_theme', True)
        }

class ThemeSettingsSerializer(serializers.Serializer):
    """Сериализатор для настроек темы"""
    primary_color = serializers.CharField(max_length=7, required=False)
    secondary_color = serializers.CharField(max_length=7, required=False)
    accent_color = serializers.CharField(max_length=7, required=False)
    bg_primary = serializers.CharField(max_length=7, required=False)
    bg_secondary = serializers.CharField(max_length=7, required=False)
    bg_card = serializers.CharField(max_length=7, required=False)
    text_primary = serializers.CharField(max_length=7, required=False)
    text_secondary = serializers.CharField(max_length=7, required=False)
    text_muted = serializers.CharField(max_length=7, required=False)
    border_color = serializers.CharField(max_length=7, required=False)
    font_family = serializers.CharField(max_length=50, required=False)
    border_radius = serializers.CharField(max_length=10, required=False)
    is_dark_theme = serializers.BooleanField(required=False)

class UserProfileSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.name', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['id', 'project', 'project_name', 'telegram_user_id', 'username', 'balance', 
                 'subscription_start', 'subscription_end', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class TarotDeckSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.name', read_only=True)
    
    class Meta:
        model = TarotDeck
        fields = ['id', 'name', 'description', 'project', 'project_name', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class TarotCardSerializer(serializers.ModelSerializer):
    deck_name = serializers.CharField(source='deck.name', read_only=True)
    
    class Meta:
        model = TarotCard
        fields = ['id', 'deck', 'deck_name', 'name', 'image', 'meaning_upright', 
                 'meaning_reversed', 'order']
        read_only_fields = ['order']

class TarotSpreadSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.name', read_only=True)
    
    class Meta:
        model = TarotSpread
        fields = ['id', 'project', 'project_name', 'name', 'description', 'num_cards', 
                 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class InterpretationSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    spread_name = serializers.CharField(source='spread.name', read_only=True)
    cards_names = serializers.SerializerMethodField()
    cards_images = serializers.SerializerMethodField()
    
    class Meta:
        model = Interpretation
        fields = ['id', 'user', 'user_username', 'spread', 'spread_name', 'cards', 
                 'cards_names', 'cards_images', 'ai_response', 'user_question', 'created_at']
        read_only_fields = ['created_at']
    
    def get_cards_names(self, obj):
        return [card.name for card in obj.cards.all()]
    
    def get_cards_images(self, obj):
        request = self.context.get('request')
        images = []
        for card in obj.cards.all():
            if card.image:
                if request is not None:
                    images.append(request.build_absolute_uri(card.image.url))
                else:
                    images.append(card.image.url)
            else:
                images.append('')
        return images

class PackageSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.name', read_only=True)
    
    class Meta:
        model = Package
        fields = ['id', 'project', 'project_name', 'name', 'package_type', 'price', 
                 'num_readings', 'subscription_days', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class PaymentSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    package_name = serializers.CharField(source='package.name', read_only=True)
    
    class Meta:
        model = Payment
        fields = ['id', 'user', 'user_username', 'project', 'project_name', 'package', 
                 'package_name', 'amount', 'status', 'external_id', 'payment_url', 
                 'created_at', 'updated_at', 'completed_at']
        read_only_fields = ['created_at', 'updated_at', 'completed_at']

class PaymentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['user', 'project', 'package', 'amount']

    def create(self, validated_data):
        # Автоматически устанавливаем сумму из пакета
        package = validated_data['package']
        validated_data['amount'] = package.price
        return super().create(validated_data) 