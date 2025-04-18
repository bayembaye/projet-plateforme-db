# accounts/views.py
from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .serializers import ProfessorProfileUpdateSerializer 
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .models import User, StudentProfile, ProfessorProfile
from .serializers import (
    UserSerializer, UserCreateSerializer, PasswordChangeSerializer,
    StudentProfileUpdateSerializer, ProfessorProfileUpdateSerializer
)
from .permissions import IsOwnerOrAdmin, IsProfessor
from django.db.models import Avg  # Ajouter en haut du fichier
from exercises.models import Exercise  # Ajouter en haut du fichier
from submissions.models import Submission  # Ajouter en haut du fichier
# Ajoutez en haut du fichier
from accounts.models import StudentPerformance
from exercises.models import ExerciseStatistics
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views import View

class UserViewSet(viewsets.ModelViewSet):
    """ViewSet pour le modèle User."""
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        """Définit les permissions pour différentes actions."""
        if self.action == 'create':
            permission_classes = [permissions.AllowAny]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsOwnerOrAdmin]
        elif self.action == 'list':
            permission_classes = [IsProfessor]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        """Retourne la classe de sérialiseur appropriée pour l'action."""
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Retourne les informations de l'utilisateur connecté."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """Permet à l'utilisateur de changer son mot de passe."""
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({"message": "Mot de passe changé avec succès."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from django.shortcuts import render
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from .permissions import IsOwnerOrAdmin
from .serializers import StudentProfileUpdateSerializer
from .models import StudentProfile

from django.shortcuts import render, get_object_or_404
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework import permissions
from .models import StudentProfile, ProfessorProfile
from .serializers import StudentProfileUpdateSerializer, ProfessorProfileUpdateSerializer
from .permissions import IsOwnerOrAdmin

from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import StudentProfileForm, ProfessorProfileForm  # Import des formulaires
from django.urls import reverse  # Import de la fonction reverse
from .models import StudentProfile, ProfessorProfile, User
from django.shortcuts import redirect
from django.contrib import messages  # Ajoutez cette ligne en haut du fichier
from django.shortcuts import redirect

class StudentProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = StudentProfile
    form_class = StudentProfileForm  # Créez ce formulaire
    template_name = 'account/student_profile_update.html'
    
    def get_object(self):
        profile, created = StudentProfile.objects.get_or_create(user=self.request.user)
        return profile
    

    def form_valid(self, form):
        # Sauvegarde du profil étudiant
        self.object = form.save()
        
        # Mise à jour des champs utilisateur
        user = self.request.user
        user.first_name = form.cleaned_data['first_name']
        user.last_name = form.cleaned_data['last_name']
        user.save()
        
        messages.success(self.request, "Profil mis à jour avec succès!")
        return redirect('account_profile')
    
    def get_success_url(self):
        return reverse('account_profile')

class ProfessorProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = ProfessorProfile
    form_class = ProfessorProfileForm  # Créez ce formulaire
    template_name = 'account/professor_profile_update.html'
   

    def get_object(self):
        profile, created = ProfessorProfile.objects.get_or_create(user=self.request.user)
        return profile
    
    def get_success_url(self):
        return reverse('account_profile')
    
    def get(self, request, *args, **kwargs):
        professor_profile = self.get_object()
        return render(request, 'account/professor_profile_update.html', {
            'user': request.user,
            'professor_profile': professor_profile,
        })
    
    def form_valid(self, form):
        # Sauvegarde du profil professeur
        self.object = form.save()
        
        # Mise à jour des champs utilisateur
        user = self.request.user
        user.first_name = form.cleaned_data['first_name']
        user.last_name = form.cleaned_data['last_name']
        user.save()
        
        messages.success(self.request, "Profil mis à jour avec succès!")
        return redirect('account_profile')

@login_required
def profile_view(request):
    context = {
        'user': request.user,
        'is_student': request.user.is_student,
        'is_professor': request.user.is_professor,
    }
    
    if request.user.is_student and hasattr(request.user, 'student_profile'):
        submissions = Submission.objects.filter(student=request.user)
        graded_submissions = submissions.filter(status='graded')
        
        context.update({
            'student_id': request.user.student_profile.student_id,
            'academic_level': request.user.student_profile.academic_level,
            'total_exercises': Exercise.objects.filter(is_active=True).count(),
            'submitted_exercises': submissions.count(),
            'pending_exercises': Exercise.objects.filter(is_active=True).count() - submissions.count(),
            'student_average': graded_submissions.aggregate(Avg('grade'))['grade__avg'],
            'feedback_distribution': {
                'Excellent': graded_submissions.filter(feedback__icontains='excellent').count(),
                'Très bien': graded_submissions.filter(feedback__icontains='très bien').count(),
                'Bien': graded_submissions.filter(feedback__icontains='bien').count(),
                'Passable': graded_submissions.filter(feedback__icontains='passable').count(),
                'Insuffisant': graded_submissions.filter(feedback__icontains='insuffisant').count(),
            }
        })
        
    elif request.user.is_professor and hasattr(request.user, 'professor_profile'):
        submissions = Submission.objects.filter(exercise__professor=request.user)
        
        context.update({
            'faculty_id': request.user.professor_profile.faculty_id,
            'department': request.user.professor_profile.department,
            'specialization': request.user.professor_profile.specialization,
            'total_submissions': submissions.count(),
            'graded_submissions': submissions.filter(status='graded').count(),
            'under_review_submissions': submissions.filter(status='under_review').count(),
            'average_grade': submissions.filter(grade__isnull=False).aggregate(Avg('grade'))['grade__avg'],
        })
    
    return render(request, 'account/profile.html', context)


from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

@login_required
@require_POST
def update_theme_preference(request):
    theme = request.POST.get('theme_preference', 'system')
    if theme in ['light', 'dark', 'system']:
        request.user.theme_preference = theme
        request.user.save()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=400)



# accounts/views.py (ajout à la fin)

from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from datetime import timedelta
from django.db.models import Avg, Count, Q
from submissions.models import Submission
from exercises.models import Exercise
from accounts.models import StudentPerformance

from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from datetime import timedelta
from django.db.models import Avg, Count, Q
from submissions.models import Submission
from accounts.models import StudentPerformance
from django.shortcuts import render
import json
from django.core.serializers.json import DjangoJSONEncoder

class StudentPerformanceView(LoginRequiredMixin, View):
    template_name = 'account/student_performance.html'
    time_period = 90  # jours d'historique

    def get(self, request):
        student = request.user
        if not student.is_student:
            return render(request, self.template_name, {'error': 'Accès réservé aux étudiants'})

        end_date = timezone.now()
        start_date = end_date - timedelta(days=self.time_period)

        submissions = Submission.objects.filter(
            student=student,
            status='graded',
            grade__isnull=False,
            submission_date__range=(start_date, end_date)
        ).select_related('exercise__category')

        if not submissions.exists():
            return render(request, self.template_name, {
                'no_data': True,
                'time_period': self.time_period
            })

        performance_data = self.calculate_performance(student, submissions)
        
        # Convertir les données pour le template
        performance_data['performance_history_json'] = json.dumps(
            performance_data['performance_history'],
            cls=DjangoJSONEncoder
        )
        
        return render(request, self.template_name, {
            'performance': performance_data,
            'time_period': self.time_period
        })

    def calculate_performance(self, student, submissions):
        # Calcul des moyennes globales
        student_avg = submissions.aggregate(avg=Avg('grade'))['avg']
        
        # Moyenne de classe
        exercise_ids = submissions.values_list('exercise_id', flat=True).distinct()
        class_avg = Submission.objects.filter(
            exercise_id__in=exercise_ids
        ).exclude(student=student).aggregate(avg=Avg('grade'))['avg'] or 0

        # Stats par catégorie
        categories = submissions.values(
            'exercise__category__name',
            'exercise__category_id'
        ).annotate(
            student_avg=Avg('grade'),
            count=Count('id')
        )

        category_stats = []
        for cat in categories:
            cat_name = cat['exercise__category__name']
            cat_id = cat['exercise__category_id']
            
            cat_exercises = submissions.filter(
                exercise__category_id=cat_id
            ).values_list('exercise_id', flat=True).distinct()
            
            cat_class_avg = Submission.objects.filter(
                exercise_id__in=cat_exercises
            ).exclude(student=student).aggregate(avg=Avg('grade'))['avg']

            category_stats.append({
                'name': cat_name,
                'student_avg': cat['student_avg'],
                'class_avg': cat_class_avg,
                'count': cat['count'],
                'difference': cat['student_avg'] - cat_class_avg if cat_class_avg else None
            })

        # Historique des performances
        performance_history = list(StudentPerformance.objects.filter(
            student=student
        ).order_by('-date').values('date', 'average_score', 'class_average')[:6])

        # Fallback si pas d'historique
        if not performance_history:
            last_submissions = submissions.order_by('-submission_date')[:6]
            performance_history = [{
                'date': sub.submission_date.date(),
                'average_score': sub.grade,
                'class_average': float(sub.grade) * 0.9  # Convert Decimal to float first
            } for sub in last_submissions]

        return {
            'student_avg': student_avg,
            'class_avg': class_avg,
            'category_stats': category_stats,
            'performance_history': performance_history,
            'submission_count': submissions.count(),
            'late_count': submissions.filter(is_late=True).count()
        }
    


