from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib.auth import get_user_model
from exercises.models import Exercise
from django_fsm import FSMField, transition
import uuid
import tempfile
import os
import logging
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from security.services.encryption import FileEncryptor, EncryptionError
from cryptography.fernet import InvalidToken
from cryptography.fernet import InvalidToken
import tempfile
import os
from django.core.exceptions import ValidationError

User = get_user_model()
logger = logging.getLogger(__name__)

class Submission(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', _('Brouillon')
        SUBMITTED = 'submitted', _('Soumis')
        UNDER_REVIEW = 'under_review', _('En révision')
        GRADED = 'graded', _('Noté')
        REJECTED = 'rejected', _('Rejeté')

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='submissions',
        verbose_name=_('étudiant')
    )
    exercise = models.ForeignKey(
        Exercise,
        on_delete=models.CASCADE,
        related_name='submissions',
        verbose_name=_('exercice')
    )
    file = models.FileField(
        upload_to='submissions/%Y/%m/%d/',
        verbose_name=_('fichier')
    )
    comment = models.TextField(
        blank=True,
        verbose_name=_('commentaire étudiant')
    )
    status = FSMField(
        default=Status.DRAFT,
        choices=Status.choices,
        verbose_name=_('statut'),
        protected=True
    )
    grade = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(20)],
        verbose_name=_('note')
    )
    feedback = models.TextField(
        blank=True,
        verbose_name=_('retour du professeur')
    )
    submission_date = models.DateTimeField(
        default=timezone.now,
        verbose_name=_('date de soumission')
    )
    last_modified = models.DateTimeField(
        auto_now=True,
        verbose_name=_('dernière modification')
    )
    is_late = models.BooleanField(
        default=False,
        verbose_name=_('en retard')
    )
    is_disputed = models.BooleanField(
        default=False,
        verbose_name=_('contestée')
    )
    dispute_reason = models.TextField(
        blank=True,
        verbose_name=_('raison de la contestation')
    )
    dispute_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('date de contestation')
    )
    auto_feedback = models.TextField(
        blank=True,
        verbose_name=_('retour automatique (IA)')
    )
    auto_grade = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(20)],
        verbose_name=_('note automatique (IA)')
    )
    auto_correction_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('date de correction automatique')
    )
    class Meta:
        verbose_name = _('soumission')
        verbose_name_plural = _('soumissions')
        ordering = ['-submission_date']
        unique_together = ['student', 'exercise']
        permissions = [
            ('can_grade_submission', 'Peut évaluer une soumission'),
            ('can_view_all_submissions', 'Peut voir toutes les soumissions'),
        ]

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.exercise.title} ({self.get_status_display()})"

    # Transitions d'état
    @transition(
        field=status,
        source=Status.DRAFT,
        target=Status.SUBMITTED,
        conditions=[lambda self: bool(self.file)],
        permission=lambda user: not user.is_professor
    )
    def submit(self):
        """Soumettre le travail"""
        self.submission_date = timezone.now()
        if self.exercise.deadline:
            self.is_late = self.submission_date > self.exercise.deadline

    @transition(
        field=status,
        source=Status.SUBMITTED,
        target=Status.UNDER_REVIEW,
        permission='submissions.can_grade_submission'
    )
    def assign_for_review(self):
        """Passer en état de révision"""
        pass

    @transition(
        field=status,
        source=Status.UNDER_REVIEW,
        target=Status.GRADED,
        permission='submissions.can_grade_submission'
    )
    def grade_submission(self, grade, feedback):
        """Noter la soumission"""
        if not isinstance(grade, (int, float)) or not 0 <= grade <= 20:
            raise ValidationError(_("La note doit être entre 0 et 20"))
        self.grade = grade
        self.feedback = feedback

    @transition(
        field=status,
        source=[Status.SUBMITTED, Status.UNDER_REVIEW],
        target=Status.REJECTED,
        permission='submissions.can_grade_submission'
    )
    def reject(self, reason):
        """Rejeter la soumission"""
        if not reason:
            raise ValidationError(_("Une raison est requise"))
        self.feedback = reason

    @transition(
        field=status,
        source=Status.GRADED,
        target=Status.UNDER_REVIEW,
        permission='submissions.can_grade_submission'
    )
    def dispute(self, reason):
        """Contester une note"""
        if not reason:
            raise ValidationError(_("Une raison est requise"))
        self.is_disputed = True
        self.dispute_reason = reason
        self.dispute_date = timezone.now()

    def clean(self):
        """Validation supplémentaire"""
        super().clean()
        
        if self.status != self.Status.DRAFT and not self.file:
            raise ValidationError(_("Un fichier est requis pour les soumissions"))
            
        if self.is_disputed and not self.dispute_reason:
            raise ValidationError(_("Une raison est requise pour les contestations"))

    @property
    def status_color(self):
        """Couleur associée au statut"""
        colors = {
            self.Status.DRAFT: 'gray',
            self.Status.SUBMITTED: 'blue',
            self.Status.UNDER_REVIEW: 'yellow',
            self.Status.GRADED: 'green',
            self.Status.REJECTED: 'red'
        }
        return colors.get(self.status, 'gray')
    
    def save(self, *args, **kwargs):
        """
        Surcharge de la méthode save pour chiffrer automatiquement les fichiers.
        """
        file_changed = self._check_file_change()
        super().save(*args, **kwargs)
        
        if file_changed and hasattr(self.file, 'path'):
            self._encrypt_uploaded_file()

    def _check_file_change(self):
        """Vérifie si le fichier a été modifié"""
        if not self.pk or self._state.adding:
            return bool(self.file)
            
        original = Submission.objects.get(pk=self.pk)
        return original.file != self.file

    def _encrypt_uploaded_file(self):
        """Chiffre le fichier uploadé"""
        try:
            encryptor = FileEncryptor()
            encryptor.encrypt_file(self.file.path)
        except Exception as e:
            logger.error(f"Failed to encrypt submission file {self.file.path}: {str(e)}")
            # On ne rollback pas la sauvegarde mais on log l'erreur

    def decrypt_file(self, input_path, output_path=None):
        """Déchiffre un fichier avec gestion robuste des erreurs"""
        if not os.path.exists(input_path):
            logger.error(f"File not found: {input_path}")
            raise FileNotFoundError(f"File not found: {input_path}")

        output_path = output_path or input_path + '.dec'
        temp_path = output_path + '.tmp'

        try:
            encryptor = FileEncryptor()
            with open(input_path, 'rb') as f:
                encrypted_data = f.read()
                if not encrypted_data:
                    logger.error(f"Empty file: {input_path}")
                    raise EncryptionError("Empty file")

            try:
                decrypted_data = encryptor.cipher.decrypt(encrypted_data)
            except InvalidToken as e:
                logger.error(f"Invalid token or corrupted file: {input_path}")
                raise EncryptionError("Invalid key or corrupted file") from e

            with open(temp_path, 'wb') as f:
                f.write(decrypted_data)

            os.replace(temp_path, output_path)
            return output_path

        except EncryptionError:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise
        except Exception as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            logger.error(f"Unexpected error during decryption: {str(e)}")
            raise EncryptionError(f"Decryption failed: {str(e)}") from e

   


    def get_decrypted_file(self):
        """Retourne un fichier temporaire déchiffré"""
        if not self.file:
            raise ValidationError("No file attached")

        temp_path = None
        try:
            encryptor = FileEncryptor()
            
            # Créer un fichier temporaire avec la bonne extension
            file_ext = os.path.splitext(self.file.name)[1]
            fd, temp_path = tempfile.mkstemp(suffix=file_ext)
            os.close(fd)

            # Déchiffrer le fichier
            decrypt_path = encryptor.decrypt_file(self.file.path, temp_path)
            
            # Retourner le fichier déchiffré
            return open(decrypt_path, 'rb')
            
        except InvalidToken:
            raise ValidationError("Invalid encryption key - please check SECURITY_ENCRYPTION_KEY in settings")
        except Exception as e:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
            raise ValidationError(f"File decryption failed: {str(e)}")

    def get_file_content(self):
        """Version robuste avec gestion du chiffrement"""
        try:
            if not self.file:
                return None

            with self.file.open('rb') as f:
                content = f.read()

            # Tentative de déchiffrement
            try:
                encryptor = FileEncryptor()
                return encryptor.cipher.decrypt(content)
            except InvalidToken:
                return content  # Non chiffré
                
        except Exception as e:
            logger.error(f"Erreur lecture fichier: {str(e)}")
            return None
    
    def get_plagiarism_scans(self):
        from plagiarism.models import PlagiarismScan
        return PlagiarismScan.objects.filter(submission=self).order_by('-created_at')

    @property
    def plagiarism_score(self):
        scan = self.get_plagiarism_scans().first()
        return scan.similarity_score if scan else None    
    
    def get_decrypted_content(self):
        """Nouvelle méthode pour récupérer le contenu déchiffré"""
        from security.services.encryption import FileEncryptor
        try:
            encryptor = FileEncryptor()
            return encryptor.decrypt_content(self.file.read())
        except Exception as e:
            logger.error(f"DECRYPT ERROR: {str(e)}")
            return None    
    
    def get_text_content(self):
        """Retourne le texte décodé du fichier avec gestion robuste de l'encodage"""
        try:
            content = self.get_file_content()
            if not content:
                return ""
            
            # Fallback simple si chardet n'est pas installé
            try:
                from chardet import detect
                encoding = detect(content)['encoding'] or 'latin-1'
            except ImportError:
                encoding = 'latin-1'  # Encodage plus permissif
            
            return content.decode(encoding, errors='replace')
        except Exception as e:
            logger.error(f"Erreur décodage fichier {self.id}: {str(e)}")
            return ""
    
    def is_valid_encrypted_file(self, file_path):
        """Vérifie si un fichier peut être déchiffré avec la clé actuelle"""
        try:
            encryptor = FileEncryptor()
            with open(file_path, 'rb') as f:
                data = f.read()
            # Juste vérifier si le fichier peut être déchiffré, sans écrire le résultat
            encryptor.cipher.decrypt(data)
            return True
        except Exception:
            return False