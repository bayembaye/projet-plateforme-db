from django.contrib import admin
from .models import SecurityEvent, EncryptionKey

@admin.register(SecurityEvent)
class SecurityEventAdmin(admin.ModelAdmin):
    list_display = ('event_type', 'user', 'timestamp')
    list_filter = ('event_type', 'timestamp')
    search_fields = ('user__username', 'details')

@admin.register(EncryptionKey)
class EncryptionKeyAdmin(admin.ModelAdmin):
    list_display = ('name', 'version', 'active', 'created_at')
    readonly_fields = ('created_at',)