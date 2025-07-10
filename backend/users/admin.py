from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'project', 'telegram_user_id', 'username', 'balance', 'subscription_start', 'subscription_end', 'created_at')
    search_fields = ('telegram_user_id', 'username')
    list_filter = ('project',)
    readonly_fields = ('created_at', 'updated_at')
