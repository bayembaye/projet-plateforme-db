from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
import uuid


class NotificationManager(models.Manager):
    def unread(self):
        """Retourne seulement les notifications non lues"""
        return self.filter(read=False)
        
    def create_user_notification(self, user, verb, description, target=None):
        """Version robuste avec gestion des UUID"""
        if target:
            return self.create(
                user=user,
                verb=verb,
                description=description,
                content_type=ContentType.objects.get_for_model(target),
                object_id=str(target.pk),  # Conversion forcée en string
                read=False
            )
        return self.create(
            user=user,
            verb=verb,
            description=description,
            read=False
        )
    
    def create_exercise_notification(self, exercise, verb, description):
        """Version avec validation renforcée des UUID"""
        if not hasattr(exercise, 'course'):
            return None
            
        try:
            # Validation stricte de l'UUID
            exercise_uuid = uuid.UUID(str(exercise.id))
            content_type = ContentType.objects.get_for_model(exercise)
            
            students = exercise.course.students.all()
            notifications = []
            
            for student in students:
                notif = self.create(
                    user=student,
                    verb=verb,
                    description=description,
                    content_type=content_type,
                    object_id=str(exercise_uuid),
                    read=False
                )
                notifications.append(notif)
                
            return notifications
            
        except ValueError as e:
            print(f"ID d'exercice invalide: {exercise.id} - {str(e)}")
            return None
        except Exception as e:
            print(f"Erreur création notification exercice: {str(e)}")
            return None


class Notification(models.Model):
    """Modèle représentant une notification utilisateur"""
    
    # L'utilisateur qui reçoit la notification
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_("utilisateur")
    )
    
    # Le type d'action (ex: "Nouvelle soumission")
    verb = models.CharField(
        max_length=255,
        verbose_name=_("action")
    )
    
    # Détails de la notification
    description = models.TextField(
        blank=True,
        verbose_name=_("description")
    )
    
    # Statut de lecture
    read = models.BooleanField(
        default=False,
        verbose_name=_("lue")
    )
    
    # Date de création
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("date de création")
    )
    
    # Système de clé générique pour lier à différents modèles
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("type de contenu")
    )
    
    object_id = models.TextField(  # Changer de CharField à TextField
        null=True,
        blank=True,
        verbose_name=_("ID de l'objet")
    )
    
    def get_absolute_url(self):
        """Version robuste de la méthode"""
        try:
            if self.target and hasattr(self.target, 'get_absolute_url'):
                return self.target.get_absolute_url()
        except:
            return reverse('notifications:list')
        return reverse('notifications:list')
    
    def save(self, *args, **kwargs):
        # Convertir l'ID en string si c'est un UUID
        if self.object_id and hasattr(self.object_id, 'hex'):
            self.object_id = str(self.object_id)
        super().save(*args, **kwargs)


       
    
    target = GenericForeignKey('content_type', 'object_id')
    
    # Utilisation du manager personnalisé
    objects = NotificationManager()
    
    class Meta:
        ordering = ['-created_at']  # Plus récentes en premier
        verbose_name = _("notification")
        verbose_name_plural = _("notifications")
    
    def __str__(self):
        return f"{self.verb} - {self.user.username}"
    
    def mark_as_read(self):
        """Marque la notification comme lue"""
        self.read = True
        self.save(update_fields=['read'])
    
    @property
    def unread(self):
        """Vérifie si la notification est non lue"""
        return not self.read
    
