from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import uuid
from submissions.models import Submission

class DocumentFingerprint(models.Model):
    submission = models.OneToOneField(
        Submission,
        on_delete=models.CASCADE,
        related_name='fingerprint'
    )
    fingerprint = models.JSONField(
        default=dict,
        help_text="Empreinte numérique du document"
    )
    tfidf_vector = models.BinaryField(
        null=True,
        blank=True,
        help_text="Vecteur TF-IDF sérialisé"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Empreinte documentaire")
        verbose_name_plural = _("Empreintes documentaires")
        permissions = [
            ('view_fingerprint', 'Peut voir les empreintes documentaires'),
        ]

    def __str__(self):
        return f"Empreinte pour {self.submission}"

class PlagiarismScan(models.Model):
    SCAN_TYPES = [
        ('INTERNAL', _('Base interne')),
        ('WEB', _('Web')),
        ('BOTH', _('Les deux'))
    ]
    STATUS_CHOICES = [
        ('PROCESSING', _('En cours')),
        ('COMPLETED', _('Terminé')),
        ('FAILED', _('Échoué'))
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    submission = models.ForeignKey(
        Submission,
        on_delete=models.CASCADE,
        related_name='scans'
    )
    scan_type = models.CharField(
        max_length=10,
        choices=SCAN_TYPES,
        default='INTERNAL'
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='PROCESSING'
    )
    similarity_score = models.FloatField(
        null=True,
        blank=True
    )
    result_data = models.JSONField(
        default=dict
    )
    error_message = models.TextField(
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = _("Scan de plagiat")
        verbose_name_plural = _("Scans de plagiat")
        permissions = [
            ('view_scan', 'Peut voir les scans de plagiat'),
            ('start_scan', 'Peut lancer des scans de plagiat'),
        ]

    def __str__(self):
        return f"Scan {self.id} - {self.submission.exercise.title}"

    def save(self, *args, **kwargs):
        if self.status == 'COMPLETED' and not self.completed_at:
            self.completed_at = timezone.now()
        super().save(*args, **kwargs)

    @property
    def is_completed(self):
        return self.status == 'COMPLETED'