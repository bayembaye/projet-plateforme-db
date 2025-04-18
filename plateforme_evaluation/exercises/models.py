from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Category(models.Model):
    """Catégorie d'exercice (ex: SQL, Modélisation, Normalisation, etc.)."""
    
    name = models.CharField(max_length=100, unique=True, verbose_name=_('nom'))
    description = models.TextField(blank=True, verbose_name=_('description'))
    
    class Meta:
        verbose_name = _('catégorie')
        verbose_name_plural = _('catégories')
    
    def __str__(self):
        return self.name


from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()

class Exercise(models.Model):
    """Exercice créé par un professeur."""
    
    class Level(models.TextChoices):
        EASY = 'EASY', _('Facile')
        MEDIUM = 'MEDIUM', _('Moyen')
        HARD = 'HARD', _('Difficile')
    
    title = models.CharField(max_length=200, verbose_name=_('titre'))
    description = models.TextField(verbose_name=_('description'))
    category = models.ForeignKey(
        'Category',
        on_delete=models.CASCADE,
        related_name='exercises',
        verbose_name=_('catégorie')
    )
    professor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='exercises_taught',
        verbose_name=_('professeur')
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_exercises',
        verbose_name=_('créé par')
    )
    difficulty_level = models.CharField(
        max_length=10,
        choices=Level.choices,
        default=Level.MEDIUM,
        verbose_name=_('niveau de difficulté')
    )
    time_limit = models.PositiveIntegerField(help_text="Durée en minutes")
    deadline = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Si c'est une nouvelle instance OU si time_limit est modifié
        if not self.pk or 'time_limit' in kwargs.get('update_fields', []):
            self.deadline = self.created_at + timezone.timedelta(minutes=self.time_limit)
        super().save(*args, **kwargs)
    deadline = models.DateTimeField(
        verbose_name=_("date limite"),
        blank=True,
        null=True,
        help_text=_("Calculée automatiquement à partir de la durée. Modifiable manuellement.")
    )
    is_active = models.BooleanField(default=True, verbose_name=_('actif'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('créé le'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('mis à jour le'))
    
    class Meta:
        verbose_name = _('exercice')
        verbose_name_plural = _('exercices')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def calculate_deadline(self):
        """Calcule la date limite en ajoutant la durée à la date de création."""
        if self.created_at and self.time_limit:
            return self.created_at + timezone.timedelta(minutes=self.time_limit)
        return None
    
    def save(self, *args, **kwargs):
        # Pour les nouvelles créations
        if not self.pk:
            super().save(*args, **kwargs)  # Sauvegarde initiale pour avoir created_at
            return
        
        # Si la durée est modifiée et que le deadline n'a pas été changé manuellement
        if 'time_limit' in kwargs.get('update_fields', []) or not self.deadline:
            calculated_deadline = self.calculate_deadline()
            if not self.deadline or self.deadline == calculated_deadline:
                self.deadline = calculated_deadline
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('exercise-detail', kwargs={'pk': self.pk})

@receiver(post_save, sender=Exercise)
def update_exercise_deadline(sender, instance, created, **kwargs):
    """Post-save hook pour calculer le deadline après la création."""
    if created and instance.time_limit:
        instance.deadline = instance.calculate_deadline()
        instance.save(update_fields=['deadline'])

class ExerciseFile(models.Model):
    """Fichier attaché à un exercice (énoncé, ressources, etc.)."""
    
    exercise = models.ForeignKey(
        Exercise,
        on_delete=models.CASCADE,
        related_name='files',
        verbose_name=_('exercice')
    )
    file = models.FileField(
        upload_to='exercise_files/',
        verbose_name=_('fichier')
    )
    file_name = models.CharField(max_length=255, verbose_name=_('nom du fichier'))
    file_type = models.CharField(max_length=100, verbose_name=_('type de fichier'))
    is_statement = models.BooleanField(
        default=False,
        help_text=_('Indique si ce fichier est l\'énoncé principal'),
        verbose_name=_('est l\'énoncé')
    )
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name=_('téléchargé le'))
    
    class Meta:
        verbose_name = _('fichier d\'exercice')
        verbose_name_plural = _('fichiers d\'exercice')
    
    def __str__(self):
        return f"{self.file_name} - {self.exercise.title}"


class Solution(models.Model):
    """Solution de référence pour un exercice, créée par un professeur."""
    
    class SolutionType(models.TextChoices):
        STANDARD = 'STANDARD', _('Standard')
        ALTERNATIVE = 'ALTERNATIVE', _('Alternative')
        SIMPLIFIED = 'SIMPLIFIED', _('Simplifiée')
        DETAILED = 'DETAILED', _('Détaillée')
    
    exercise = models.ForeignKey(
        Exercise,
        on_delete=models.CASCADE,
        related_name='solutions',
        verbose_name=_('exercice')
    )
    title = models.CharField(
        max_length=200,
        verbose_name=_('titre du modèle'),
        help_text=_("Donnez un nom explicite à ce modèle de correction"),
        blank=False
    )
    solution_type = models.CharField(
        max_length=20,
        choices=SolutionType.choices,
        default=SolutionType.STANDARD,
        verbose_name=_('type de solution')
    )
    description = models.TextField(verbose_name=_('description'))
    file = models.FileField(
        upload_to='solutions/',
        blank=True,
        null=True,
        verbose_name=_('fichier')
    )
    is_default = models.BooleanField(
        default=False,
        verbose_name=_('modèle par défaut'),
        help_text=_("Utiliser ce modèle comme correction de référence")
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('créé le'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('mis à jour le'))
    
    class Meta:
        verbose_name = _('solution')
        verbose_name_plural = _('solutions')
        ordering = ['-is_default', 'solution_type']
    
    def __str__(self):
        return f"{self.title} - {self.exercise.title}"

    def save(self, *args, **kwargs):
        # S'assurer qu'il n'y a qu'un seul modèle par défaut
        if self.is_default:
            Solution.objects.filter(
                exercise=self.exercise
            ).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)

class ExerciseGroup(models.Model):
    """Groupe d'exercices pour une classe ou un cours spécifique."""
    
    title = models.CharField(max_length=200, verbose_name=_('titre'))
    description = models.TextField(blank=True, verbose_name=_('description'))
    professor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_groups',
        verbose_name=_('professeur')
    )
    exercises = models.ManyToManyField(
        Exercise,
        related_name='groups',
        verbose_name=_('exercices')
    )
    start_date = models.DateTimeField(verbose_name=_('date de début'))
    end_date = models.DateTimeField(verbose_name=_('date de fin'))
    is_active = models.BooleanField(default=True, verbose_name=_('actif'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('créé le'))
    
    class Meta:
        verbose_name = _('groupe d\'exercices')
        verbose_name_plural = _('groupes d\'exercices')
    
    def __str__(self):
        return self.title
    

class ExerciseStatistics(models.Model):
    """Statistiques pour un exercice spécifique."""
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name='statistics')
    average_grade = models.FloatField()
    submission_count = models.PositiveIntegerField()
    completion_rate = models.FloatField()
    common_errors = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('statistique exercice')
        verbose_name_plural = _('statistiques exercices')

    def __str__(self):
        return f"Stats pour {self.exercise.title}"
    
    # exercises/models.py (ajouter cette méthode à la classe Exercise)
def get_absolute_url(self):
    return reverse('exercise-detail', kwargs={'pk': self.pk})
