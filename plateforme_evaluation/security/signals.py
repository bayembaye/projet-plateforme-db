from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import SecurityEvent
from django.utils import timezone

User = get_user_model()

@receiver(post_save, sender=User)
def log_user_change(sender, instance, created, **kwargs):
    # Gestion robuste des update_fields
    update_fields = kwargs.get('update_fields', set())
    
    # Conversion en liste si nécessaire
    if isinstance(update_fields, (frozenset, set)):
        changed_fields = list(update_fields)
    else:
        changed_fields = []

    # Pour les créations, on peut logger tous les champs initiaux
    if created:
        changed_fields = [f.name for f in sender._meta.fields 
                         if f.name != 'id' and getattr(instance, f.name) is not None]

    SecurityEvent.objects.create(
        event_type='USER_CREATED' if created else 'USER_UPDATED',
        user=instance,
        ip_address='127.0.0.1',  # À remplacer par l'IP réelle si disponible
        details={
            'action': 'create' if created else 'update',
            'changed_fields': changed_fields,
            'timestamp': timezone.now().isoformat(),
            'model': f'{sender.__module__}.{sender.__name__}'
        }
    )