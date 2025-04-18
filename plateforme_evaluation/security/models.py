from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class SecurityEvent(models.Model):
    EVENT_TYPES = (
        ('AUTH', 'Authentification'),
        ('FILE_OP', 'Opération fichier'),
        ('KEY_MGMT', 'Gestion de clés'),
        ('SYS', 'Système'),
    )
    
    event_type = models.CharField(max_length=10, choices=EVENT_TYPES)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    ip_address = models.GenericIPAddressField(null=True, blank=True)  # Rendre le champ optionnel
    user_agent = models.TextField(blank=True)
    details = models.JSONField(default=dict, encoder=None)  # Désactive l'encodeur par défaut
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Événement de sécurité"
        verbose_name_plural = "Événements de sécurité"
    
    def __str__(self):
        return f"{self.get_event_type_display()} - {self.timestamp}"

class EncryptionKey(models.Model):
    name = models.CharField(max_length=100)
    key_material = models.BinaryField()  # Stockage sécurisé
    version = models.PositiveIntegerField(unique=True)
    active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Clé de chiffrement"
        verbose_name_plural = "Clés de chiffrement"
    
    def __str__(self):
        return f"{self.name} (v{self.version})"