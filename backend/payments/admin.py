from django.contrib import admin
from .models import Package, Payment

@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'project', 'package_type', 'price', 'num_readings', 'subscription_days', 'is_active', 'created_at')
    search_fields = ('name',)
    list_filter = ('project', 'package_type', 'is_active')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'project', 'package', 'amount', 'status', 'created_at', 'completed_at')
    search_fields = ('user__username', 'external_id')
    list_filter = ('project', 'status', 'package')
    readonly_fields = ('created_at', 'updated_at', 'completed_at')
    actions = ['mark_as_completed', 'mark_as_failed', 'mark_as_cancelled']

    def mark_as_completed(self, request, queryset):
        for payment in queryset:
            payment.mark_as_completed()
        self.message_user(request, f"{queryset.count()} платежей отмечено как завершенные")
    mark_as_completed.short_description = "Отметить как завершенные"

    def mark_as_failed(self, request, queryset):
        for payment in queryset:
            payment.mark_as_failed()
        self.message_user(request, f"{queryset.count()} платежей отмечено как неудачные")
    mark_as_failed.short_description = "Отметить как неудачные"

    def mark_as_cancelled(self, request, queryset):
        for payment in queryset:
            payment.mark_as_cancelled()
        self.message_user(request, f"{queryset.count()} платежей отмечено как отмененные")
    mark_as_cancelled.short_description = "Отметить как отмененные"
