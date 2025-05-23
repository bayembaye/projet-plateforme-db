# accounts/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, StudentProfile, ProfessorProfile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Crée le profil approprié lorsqu'un nouvel utilisateur est créé."""
    if created:
        if instance.role == User.Role.STUDENT:
            StudentProfile.objects.create(user=instance)
        elif instance.role == User.Role.PROFESSOR:
            ProfessorProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Sauvegarde le profil lorsque l'utilisateur est mis à jour."""
    if instance.role == User.Role.STUDENT:
        # Assure-toi que le profil étudiant existe
        if not hasattr(instance, 'student_profile'):
            StudentProfile.objects.create(user=instance)
        instance.student_profile.save()
    elif instance.role == User.Role.PROFESSOR:
        # Assure-toi que le profil professeur existe
        if not hasattr(instance, 'professor_profile'):
            ProfessorProfile.objects.create(user=instance)
        instance.professor_profile.save()