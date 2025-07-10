from rest_framework import serializers
from projects.models import Project
from users.models import UserProfile
from tarot.models import TarotDeck, TarotCard, TarotSpread, Interpretation
from payments.models import Package, Payment

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'telegram_token', 'design', 'status', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

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
                 'cards_names', 'cards_images', 'ai_response', 'created_at']
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