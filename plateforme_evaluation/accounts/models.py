# accounts/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.exceptions import ValidationError


class UserManager(BaseUserManager):
    """Manager personnalisé pour le modèle User."""
    
    def create_user(self, email, password=None, **extra_fields):
        """Crée et sauvegarde un utilisateur avec l'email et le mot de passe donnés."""
        if not email:
            raise ValueError(_('Un email est requis'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Crée et sauvegarde un superutilisateur."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'PROFESSOR')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Le superutilisateur doit avoir is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Le superutilisateur doit avoir is_superuser=True.'))
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):

    class ThemePreference(models.TextChoices):
        LIGHT = 'light', _('Clair')
        DARK = 'dark', _('Sombre')
        SYSTEM = 'system', _('Système')
    
    theme_preference = models.CharField(
        max_length=10,
        choices=ThemePreference.choices,
        default=ThemePreference.SYSTEM,
        verbose_name=_('préférence de thème')
    )
   
    
    """Modèle utilisateur personnalisé avec email comme identifiant unique."""
    
    class Role(models.TextChoices):
        STUDENT = 'STUDENT', _('Étudiant')
        PROFESSOR = 'PROFESSOR', _('Professeur')
    
    username = None
    email = models.EmailField(_('adresse email'), unique=True)
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.STUDENT,
        verbose_name=_('rôle')
    )
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True,
        verbose_name=_('photo de profil')
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('créé le'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('mis à jour le'))
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    class Meta:
        verbose_name = _('utilisateur')
        verbose_name_plural = _('utilisateurs')
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}" if self.first_name and self.last_name else self.email
    
    @property
    def is_student(self):
        return self.role == self.Role.STUDENT
    
    @property
    def is_professor(self):
        return self.role == self.Role.PROFESSOR
    def can_submit(self, exercise):
        """Vérifie si la soumission est possible avant la deadline"""
        if not exercise.deadline:
            return True
        return timezone.now() <= exercise.deadline 

class StudentProfile(models.Model):
    """Profil étudiant avec informations supplémentaires."""
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='student_profile',
        verbose_name=_('utilisateur')
    )
    student_id = models.CharField(
        max_length=50, 
        unique=True, 
        blank=True, 
        null=True,
        verbose_name=_('numéro étudiant')
    )
    academic_level = models.CharField(
        max_length=100, 
        blank=True, 
        verbose_name=_('niveau académique')
    )
    
    class Meta:
        verbose_name = _('profil étudiant')
        verbose_name_plural = _('profils étudiants')
    
    def __str__(self):
        return f"Profil étudiant de {self.user.email}"


class ProfessorProfile(models.Model):
    """Profil professeur avec informations supplémentaires."""
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='professor_profile',
        verbose_name=_('utilisateur')
    )
    faculty_id = models.CharField(
        max_length=50, 
        unique=True, 
        blank=True, 
        null=True,
        verbose_name=_('numéro faculté')
    )
    department = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name=_('département')
    )
    specialization = models.CharField(
        max_length=200, 
        blank=True,
        verbose_name=_('spécialisation')
    )
    
    class Meta:
        verbose_name = _('profil professeur')
        verbose_name_plural = _('profils professeurs')
    
    def __str__(self):
        return f"Profil professeur de {self.user.email}"
    

# accounts/models.py (ajout à la fin)

class StudentPerformance(models.Model):
    """Stocke les statistiques de performance des étudiants."""
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='performances')
    date = models.DateField(auto_now_add=True)
    average_score = models.FloatField()
    class_average = models.FloatField()
    improvement_rate = models.FloatField(null=True, blank=True)
    category_breakdown = models.JSONField(default=dict)
    submission_count = models.PositiveIntegerField(default=0)
    late_submissions = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = _('performance étudiant')
        verbose_name_plural = _('profils étudiants')
        ordering = ['-date']

    def __str__(self):
        return f"Performance de {self.student.email} - {self.date}"

