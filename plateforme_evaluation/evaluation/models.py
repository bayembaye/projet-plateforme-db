# evaluation/models.py

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from submissions.models import Submission


class Evaluation(models.Model):
    """Évaluation d'une soumission par l'IA ou un professeur."""
    
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('En attente')
        PROCESSING = 'PROCESSING', _('En cours de traitement')
        COMPLETED = 'COMPLETED', _('Complétée')
        FAILED = 'FAILED', _('Échouée')
    
    submission = models.OneToOneField(
        Submission,
        on_delete=models.CASCADE,
        related_name='evaluation',
        verbose_name=_('soumission')
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name=_('statut')
    )
    ai_score = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(20)],
        null=True,
        blank=True,
        verbose_name=_('note IA')
    )
    final_score = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(20)],
        null=True,
        blank=True,
        verbose_name=_('note finale')
    )
    ai_feedback = models.TextField(blank=True, verbose_name=_('retour IA'))
    professor_feedback = models.TextField(blank=True, verbose_name=_('retour professeur'))
    evaluated_at = models.DateTimeField(auto_now_add=True, verbose_name=_('évalué le'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('mis à jour le'))
    is_reviewed_by_professor = models.BooleanField(default=False, verbose_name=_('revu par le professeur'))
    
    class Meta:
        verbose_name = _('évaluation')
        verbose_name_plural = _('évaluations')
    
    def __str__(self):
        return f"Évaluation de {self.submission.student.email} pour {self.submission.exercise.title}"


class FeedbackItem(models.Model):
    """Élément spécifique de retour détaillé sur une évaluation."""
    
    class Type(models.TextChoices):
        POSITIVE = 'POSITIVE', _('Positif')
        NEGATIVE = 'NEGATIVE', _('Négatif')
        SUGGESTION = 'SUGGESTION', _('Suggestion')
    
    evaluation = models.ForeignKey(
        Evaluation,
        on_delete=models.CASCADE,
        related_name='feedback_items',
        verbose_name=_('évaluation')
    )
    type = models.CharField(
        max_length=20,
        choices=Type.choices,
        verbose_name=_('type')
    )
    content = models.TextField(verbose_name=_('contenu'))
    order = models.PositiveIntegerField(default=0, verbose_name=_('ordre'))
    
    class Meta:
        verbose_name = _('élément de retour')
        verbose_name_plural = _('éléments de retour')
        ordering = ['order']
    
    def __str__(self):
        return f"{self.get_type_display()} pour {self.evaluation.submission.exercise.title}"


class PerformanceAnalytics(models.Model):
    """Analyse des performances d'un étudiant sur tous les exercices."""
    
    student = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='performance_analytics',
        verbose_name=_('étudiant')
    )
    average_score = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(20)],
        default=0,
        verbose_name=_('note moyenne')
    )
    total_submissions = models.PositiveIntegerField(default=0, verbose_name=_('total des soumissions'))
    strengths = models.TextField(blank=True, verbose_name=_('points forts'))
    weaknesses = models.TextField(blank=True, verbose_name=_('points faibles'))
    improvement_suggestions = models.TextField(blank=True, verbose_name=_('suggestions d\'amélioration'))
    last_updated = models.DateTimeField(auto_now=True, verbose_name=_('dernière mise à jour'))
    
    class Meta:
        verbose_name = _('analyse de performance')
        verbose_name_plural = _('analyses de performances')
    
    def __str__(self):
        return f"Analyse de performance de {self.student.email}"