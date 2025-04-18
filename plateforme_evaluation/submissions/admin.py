# admin.py
from django.contrib import admin
from .models import Submission

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    readonly_fields = ('status',)  # Empêche la modification directe du statut
    # Autres configurations...