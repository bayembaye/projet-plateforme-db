# exercises/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from .models import Exercise
from notifications.models import Notification
import uuid
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

@receiver(post_save, sender=Exercise)
def handle_exercise_notifications(sender, instance, created, **kwargs):
    """Gestion des notifications pour les exercices envoyées à tous les étudiants"""
    try:
        # Validation de l'ID
        exercise_uuid = uuid.UUID(str(instance.id))
        content_type = ContentType.objects.get_for_model(instance)
        
        if created:
            # Notification pour le professeur créateur
            Notification.objects.create(
                user=instance.professor,
                verb="Nouvel exercice créé",
                description=f"Vous avez créé un nouvel exercice: {instance.title}",
                content_type=content_type,
                object_id=str(exercise_uuid),
                read=False
            )
            
            # Notification pour tous les étudiants
            students = User.objects.filter(is_professor=False)  # Ou le filtre approprié pour vos étudiants
            for student in students:
                Notification.objects.create(
                    user=student,
                    verb="Nouvel exercice disponible",
                    description=f"Un nouvel exercice est disponible: {instance.title}",
                    content_type=content_type,
                    object_id=str(exercise_uuid),
                    read=False
                )
            
        elif instance.is_active and 'is_active' in kwargs.get('update_fields', []):
            # Notification lorsque l'exercice est activé/pubié
            students = User.objects.filter(is_professor=False)
            for student in students:
                Notification.objects.create(
                    user=student,
                    verb="Exercice publié",
                    description=f"Un exercice est maintenant disponible: {instance.title}",
                    content_type=content_type,
                    object_id=str(exercise_uuid),
                    read=False
                )
                    
    except ValueError as e:
        logger.error(f"ID d'exercice invalide: {instance.id} - {str(e)}")
    except Exception as e:
        logger.error(f"Erreur création notification exercice: {str(e)}")