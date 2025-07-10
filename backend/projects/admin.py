from django.contrib import admin
from .models import Project

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'status', 'created_at')
    search_fields = ('name', 'telegram_token')
    list_filter = ('status',)
    readonly_fields = ('created_at', 'updated_at')
