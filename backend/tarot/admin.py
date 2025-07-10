from django.contrib import admin
from .models import TarotDeck, TarotCard, TarotSpread, Interpretation

@admin.register(TarotDeck)
class TarotDeckAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'project', 'created_at')
    search_fields = ('name',)
    list_filter = ('project',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(TarotCard)
class TarotCardAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'deck', 'order')
    search_fields = ('name',)
    list_filter = ('deck',)

@admin.register(TarotSpread)
class TarotSpreadAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'project', 'num_cards', 'created_at')
    search_fields = ('name',)
    list_filter = ('project',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Interpretation)
class InterpretationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'spread', 'created_at')
    search_fields = ('user__username', 'spread__name')
    list_filter = ('spread', 'user')
    readonly_fields = ('created_at',)
