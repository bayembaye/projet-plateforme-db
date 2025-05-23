# accounts/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, StudentProfile, ProfessorProfile
# Ajoutez en haut du fichier
from accounts.models import StudentPerformance
from exercises.models import ExerciseStatistics

class StudentProfileInline(admin.StackedInline):
    model = StudentProfile
    can_delete = False
    verbose_name_plural = _('profil étudiant')


class ProfessorProfileInline(admin.StackedInline):
    model = ProfessorProfile
    can_delete = False
    verbose_name_plural = _('profil professeur')


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin pour le modèle User personnalisé."""
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Informations personnelles'), {'fields': ('first_name', 'last_name', 'role', 'profile_picture')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Dates importantes'), {'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role'),
        }),
    )
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'role', 'groups')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    readonly_fields = ('created_at', 'updated_at')
    
    def get_inlines(self, request, obj=None):
        if obj:
            if obj.role == User.Role.STUDENT:
                return [StudentProfileInline]
            elif obj.role == User.Role.PROFESSOR:
                return [ProfessorProfileInline]
        return []


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    """Admin pour le modèle StudentProfile."""
    
    list_display = ('user', 'student_id', 'academic_level')
    search_fields = ('user__email', 'student_id', 'academic_level')
    raw_id_fields = ('user',)


@admin.register(ProfessorProfile)
class ProfessorProfileAdmin(admin.ModelAdmin):
    """Admin pour le modèle ProfessorProfile."""
    
    list_display = ('user', 'faculty_id', 'department', 'specialization')
    search_fields = ('user__email', 'faculty_id', 'department', 'specialization')
    raw_id_fields = ('user',)

# accounts/admin.py (ajout à la fin)

@admin.register(StudentPerformance)
class StudentPerformanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'average_score', 'class_average', 'improvement_rate')
    list_filter = ('date', 'student')
    search_fields = ('student__email', 'student__first_name', 'student__last_name')
    readonly_fields = ('category_breakdown',)

@admin.register(ExerciseStatistics)
class ExerciseStatisticsAdmin(admin.ModelAdmin):
    list_display = ('exercise', 'average_grade', 'submission_count', 'completion_rate')
    list_filter = ('exercise__professor', 'exercise__category')
    search_fields = ('exercise__title',)
    readonly_fields = ('common_errors',)    