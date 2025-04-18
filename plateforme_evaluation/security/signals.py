from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import SecurityEvent
from django.utils import timezone

User = get_user_model()

@receiver(post_save, sender=User)
def log_user_change(sender, instance, created, **kwargs):
    update_fields = kwargs.get('update_fields')
    if update_fields and isinstance(update_fields, (frozenset, set)):
        kwargs['update_fields'] = list(update_fields)
    
    SecurityEvent.objects.create(
        event_type='AUTH' if created else 'USER_MOD',
        user=instance,
        ip_address='127.0.0.1',
        details={
            'action': 'create' if created else 'update',
            'changed_fields': list(kwargs.get('update_fields', [])),
            'timestamp': timezone.now().isoformat()
        }
    )