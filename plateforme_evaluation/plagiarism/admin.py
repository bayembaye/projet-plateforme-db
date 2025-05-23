from django.contrib import admin
from .models import PlagiarismScan, DocumentFingerprint

@admin.register(PlagiarismScan)
class PlagiarismScanAdmin(admin.ModelAdmin):
    list_display = ('id', 'submission', 'scan_type', 'similarity_score', 'created_at')
    list_filter = ('scan_type', 'created_at')
    search_fields = (
        'submission__exercise__title',
        'submission__student__username',
        'submission__student__email'
    )
    readonly_fields = ('result_data',)
    date_hierarchy = 'created_at'

@admin.register(DocumentFingerprint)
class DocumentFingerprintAdmin(admin.ModelAdmin):
    list_display = ('submission', 'created_at')
    search_fields = (
        'submission__exercise__title', 
        'submission__student__username'
    )