from django.apps import AppConfig


class SecurityConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'security'

    def ready(self):
        from django.contrib.auth.models import Permission, Group
        from django.contrib.contenttypes.models import ContentType
        
        content_type = ContentType.objects.get_for_model(SecurityEvent)
        
        Permission.objects.get_or_create(
            codename='view_securityevent',
            name='Can view security events',
            content_type=content_type
        )
    
    def ready(self):
        # Importer les signaux
        from . import signals  # Créez ce fichier si besoin