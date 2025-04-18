from django.db.models.signals import post_save
from django.dispatch import receiver
from submissions.models import Submission
from notifications.models import Notification

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from .models import Submission
from notifications.models import Notification
import logging
import uuid

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Submission)
def submission_notification(sender, instance, created, **kwargs):
    """Gère les notifications liées aux soumissions"""
    try:
        if instance.status == 'graded' and instance.student:
            # Utilisation directe de l'UUID comme string
            Notification.objects.create(
                user=instance.student,
                verb="Soumission notée",
                description=f"Votre soumission a reçu une note: {instance.grade}/20",
                content_type=ContentType.objects.get_for_model(instance),
                object_id=str(instance.pk),  # Conversion en string
                read=False
            )
    except Exception as e:
        logger.error(f"Erreur création notification: {str(e)}")