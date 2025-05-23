from django.views.generic import (
    ListView, 
    DetailView, 
    CreateView, 
    UpdateView,
    DeleteView
)
from submissions.models import Submission  # Ajoutez cette ligne en haut du fichier
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect  # Pour la redirection
from django.views import View  # Pour la vue basée sur les classes
from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django import forms
from .models import Exercise, ExerciseFile, Solution, ExerciseGroup, Category
from .serializers import (
    ExerciseSerializer,
    ExerciseFileSerializer,
    SolutionSerializer,
    ExerciseGroupSerializer,
    CategorySerializer
)
from accounts.permissions import IsProfessor

from django.views import View
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Avg, Count, Q
from exercises.models import Exercise, ExerciseStatistics
from submissions.models import Submission
from accounts.models import User

from django.utils import timezone

def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['timezone_now'] = timezone.now()
    return context

# ====================== FORMULAIRES ======================

class ExerciseFileForm(forms.ModelForm):
    class Meta:
        model = ExerciseFile
        fields = ['file', 'file_name', 'file_type', 'is_statement']
        widgets = {
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.txt,.zip,.sql,.py'
            }),
            'file_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom descriptif du fichier'
            }),
            'file_type': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: PDF, SQL, Python, etc.'
            }),
            'is_statement': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            max_size = 20 * 1024 * 1024  # 20MB
            if file.size > max_size:
                raise forms.ValidationError(f"Le fichier est trop volumineux. Taille maximale: {max_size/1024/1024}MB.")
            
            valid_extensions = ['.pdf', '.doc', '.docx', '.txt', '.zip', '.sql', '.py']
            if not any(file.name.lower().endswith(ext) for ext in valid_extensions):
                raise forms.ValidationError("Type de fichier non supporté. Formats acceptés: PDF, DOC, TXT, ZIP, SQL, PY.")
        return file

class SolutionForm(forms.ModelForm):
    class Meta:
        model = Solution
        fields = ['title', 'solution_type', 'description', 'file', 'is_default']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Correction standard, Solution alternative, etc.'
            }),
            'solution_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Description détaillée de la solution'
            }),
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.py,.sql,.txt,.doc,.docx'
            }),
            'is_default': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

# ====================== API VIEWSETS ======================

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class ExerciseViewSet(viewsets.ModelViewSet):
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsProfessor]
        else:
            permission_classes = [permissions.IsAuthenticatedOrReadOnly]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(professor=self.request.user)

    @action(detail=True, methods=['get'])
    def files(self, request, pk=None):
        exercise = self.get_object()
        files = exercise.files.all()
        serializer = ExerciseFileSerializer(files, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        recent_exercises = Exercise.objects.filter(is_active=True).order_by('-created_at')[:5]
        serializer = self.get_serializer(recent_exercises, many=True)
        return Response(serializer.data)

class ExerciseFileViewSet(viewsets.ModelViewSet):
    queryset = ExerciseFile.objects.all()
    serializer_class = ExerciseFileSerializer
    permission_classes = [IsProfessor]

class SolutionViewSet(viewsets.ModelViewSet):
    queryset = Solution.objects.all()
    serializer_class = SolutionSerializer
    permission_classes = [IsProfessor]

class ExerciseGroupViewSet(viewsets.ModelViewSet):
    queryset = ExerciseGroup.objects.all()
    serializer_class = ExerciseGroupSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsProfessor]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(professor=self.request.user)

# ====================== TEMPLATE VIEWS ======================

class ExerciseListView(LoginRequiredMixin, ListView):
    model = Exercise
    template_name = 'exercises/exercise_list.html'
    context_object_name = 'exercises'
    
    def get_queryset(self):
        queryset = Exercise.objects.filter(is_active=True)
        
        # Filtre pour ne voir que ses exercices si c'est un professeur
        if self.request.user.is_professor:
            queryset = queryset.filter(professor=self.request.user)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_professor:
            context['categories'] = Category.objects.filter(
                exercises__professor=self.request.user
            ).distinct()
        else:
            context['categories'] = Category.objects.all()
        return context

class ExerciseCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Exercise
    template_name = 'exercises/exercise_form.html'
    fields = ['title', 'description', 'category', 'difficulty_level', 'time_limit']
    
    def test_func(self):
        return self.request.user.is_professor
    
    def form_valid(self, form):
        form.instance.professor = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('exercise-detail', kwargs={'pk': self.object.pk})

class ExerciseDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Exercise
    template_name = 'exercises/exercise_confirm_delete.html'
    success_url = reverse_lazy('exercise-list')
    
    def test_func(self):
        return self.request.user.is_professor and self.get_object().professor == self.request.user

class ExerciseUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Exercise
    template_name = 'exercises/exercise_form.html'
    fields = ['title', 'description', 'category', 'difficulty_level', 'time_limit', 'is_active']
    def form_valid(self, form):
        # Force la mise à jour du deadline si time_limit change
        if 'time_limit' in form.changed_data:
            self.object.deadline = self.object.created_at + timezone.timedelta(minutes=form.cleaned_data['time_limit'])
        return super().form_valid(form)
    def test_func(self):
        exercise = self.get_object()
        return self.request.user.is_professor and exercise.professor == self.request.user

class ExerciseDetailView(DetailView):
    model = Exercise
    template_name = 'exercises/exercise_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        exercise = self.get_object()
        context['files'] = exercise.files.all()  # Ceci est crucial
        
        # Calcul des heures pour l'affichage
        context['hours'] = exercise.time_limit / 60
        context['timezone_now'] = timezone.now()
        
        # Gestion des permissions
        context['is_owner'] = self.request.user == exercise.professor
        context['solutions'] = exercise.solutions.all()
            # Debug des solutions
        print(f"Solutions trouvées pour l'exercice {exercise.id}:")
        for sol in exercise.solutions.all():
            print(f"- {sol.title} (ID: {sol.id})")
        
        context['solutions'] = exercise.solutions.all()

        # Pour les étudiants
        if not self.request.user.is_professor:
            context['user_submission'] = Submission.objects.filter(
                student=self.request.user,
                exercise=exercise
            ).first()
        
        # Pour les professeurs propriétaires
        if context['is_owner']:
            context['submissions'] = Submission.objects.filter(
                exercise=exercise
            ).select_related('student')
            
        return context
    
def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    if self.request.user.is_authenticated:
        context['unread_notifications_count'] = self.request.user.notifications.unread().count()
    return context
class ExerciseFileCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = ExerciseFile
    form_class = ExerciseFileForm
    template_name = 'exercises/exercisefile_form.html'

    def test_func(self):
        exercise = get_object_or_404(Exercise, pk=self.kwargs['exercise_id'])
        return self.request.user.is_professor and exercise.professor == self.request.user

    def form_valid(self, form):
        exercise = get_object_or_404(Exercise, pk=self.kwargs['exercise_id'])
        form.instance.exercise = exercise
        form.instance.uploaded_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('exercise-detail', kwargs={'pk': self.kwargs['exercise_id']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['exercise'] = get_object_or_404(Exercise, pk=self.kwargs['exercise_id'])
        return context

class ExerciseFileDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = ExerciseFile
    template_name = 'exercises/exercisefile_confirm_delete.html'

    def test_func(self):
        file = self.get_object()
        return self.request.user.is_professor and file.exercise.professor == self.request.user

    def get_success_url(self):
        return reverse('exercise-detail', kwargs={'pk': self.object.exercise.pk})

class SolutionCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Solution
    form_class = SolutionForm
    template_name = 'exercises/solution_form.html'

    def test_func(self):
        exercise = get_object_or_404(Exercise, pk=self.kwargs['exercise_id'])
        return self.request.user.is_professor and exercise.professor == self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['exercise'] = get_object_or_404(Exercise, pk=self.kwargs['exercise_id'])
        return context

    def form_valid(self, form):
        form.instance.exercise = get_object_or_404(Exercise, pk=self.kwargs['exercise_id'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('exercise-detail', kwargs={'pk': self.kwargs['exercise_id']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        exercise = get_object_or_404(Exercise, pk=self.kwargs['exercise_id'])
        context['exercise'] = exercise
        context['existing_solutions'] = exercise.solutions.all()
        return context
    
class SetDefaultSolutionView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        solution = get_object_or_404(Solution, pk=self.kwargs['pk'])
        return self.request.user.is_professor and solution.exercise.professor == self.request.user

    def post(self, request, *args, **kwargs):
        solution = get_object_or_404(Solution, pk=self.kwargs['pk'])
        Solution.objects.filter(exercise=solution.exercise).update(is_default=False)
        solution.is_default = True
        solution.save()
        return redirect('exercise-detail', pk=solution.exercise.pk)

class ExerciseGroupCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = ExerciseGroup
    template_name = 'exercises/group_form.html'
    fields = ['title', 'description', 'exercises', 'start_date', 'end_date']
    
    def test_func(self):
        return self.request.user.is_professor
    
    def form_valid(self, form):
        form.instance.professor = self.request.user
        return super().form_valid(form)

class CategoryCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Category
    fields = ['name', 'description']
    template_name = 'exercises/category_form.html'
    success_url = reverse_lazy('exercise-create')

    def test_func(self):
        return self.request.user.is_professor
    


from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render
from django.db.models import Avg, Count, Q, F
from django.db.models.functions import TruncWeek
from exercises.models import Exercise
from submissions.models import Submission
from accounts.models import User
from django.utils import timezone
from datetime import timedelta
from collections import Counter
import json

from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render
from django.db.models import Avg, Count, Q, F
from django.db.models.functions import TruncWeek
from exercises.models import Exercise
from submissions.models import Submission
from accounts.models import User
from django.utils import timezone
from datetime import timedelta
from collections import Counter
import json
import re  # Import manquant ajouté ici

class ProfessorStatisticsView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = 'exercises/professor_stats.html'  # Nom inchangé

    def test_func(self):
        return self.request.user.is_professor

    def get(self, request):
        professor = request.user
        exercises = Exercise.objects.filter(professor=professor)
        submissions = Submission.objects.filter(exercise__in=exercises)
        
        if not submissions.exists():
            return render(request, self.template_name, {'no_data': True})

        stats = {
            'general_stats': self._get_general_stats(exercises, submissions),
            'exercise_stats': self._get_exercise_stats(exercises),
            'common_errors': self._get_common_errors(submissions),
            'submission_trends': self._get_submission_trends(submissions),
            'student_performance': self._get_student_performance(submissions)
        }
        
        stats['submission_trends_json'] = json.dumps(
            self._format_trends_for_js(stats['submission_trends']),
            default=str
        )
        
        return render(request, self.template_name, {'stats': stats})

    def _get_general_stats(self, exercises, submissions):
        graded = submissions.filter(status='graded')
        return {
            'total_exercises': exercises.count(),
            'total_submissions': submissions.count(),
            'submission_rate': (submissions.values('exercise').distinct().count() / exercises.count()) * 100,
            'average_grade': graded.aggregate(avg=Avg('grade'))['avg'],
            'late_submissions': submissions.filter(is_late=True).count()
        }

    def _get_exercise_stats(self, exercises):
        stats = []
        for exercise in exercises:
            exercise_subs = exercise.submissions.all()
            if exercise_subs.exists():
                graded = exercise_subs.filter(status='graded')
                stats.append({
                    'exercise': exercise,
                    'submission_count': exercise_subs.count(),
                    'average_grade': graded.aggregate(avg=Avg('grade'))['avg'],
                    'completion_rate': (exercise_subs.values('student').distinct().count() / 
                                      User.objects.filter(role='STUDENT').count()) * 100,
                    'difficulty_index': self._calculate_difficulty_index(graded)
                })
        return stats

    def _calculate_difficulty_index(self, submissions):
        if submissions.count() > 0:
            avg_grade = submissions.aggregate(avg=Avg('grade'))['avg']
            return (1 - (avg_grade / 20)) * 100
        return 0

    def _get_common_errors(self, submissions):
        feedbacks = submissions.exclude(
            Q(feedback__isnull=True) | Q(feedback__exact='')
        ).values_list('feedback', flat=True)
        
        if not feedbacks:
            return []
        
        error_patterns = [
            ('erreur de calcul', r'calcul|arithmétique|opération'),
            ('problème de syntaxe', r'syntaxe|orthographe|grammaire'),
            ('incompréhension', r'comprendre|interpréter|confus'),
            ('manque de précision', r'précision|détaill|complétude'),
            ('méthode incorrecte', r'méthode|approche|procédure')
        ]
        
        error_counts = Counter()
        
        for feedback in feedbacks:
            feedback_lower = feedback.lower()
            for error_name, pattern in error_patterns:
                if re.search(pattern, feedback_lower):
                    error_counts[error_name] += 1
                    break
        
        return error_counts.most_common(5)

    def _get_submission_trends(self, submissions):
        trends = submissions.annotate(
            week=TruncWeek('submission_date')
        ).values('week').annotate(
            total=Count('id'),
            graded=Count('id', filter=Q(status='graded')),
            late=Count('id', filter=Q(is_late=True))
        ).order_by('week')
        
        return list(trends)

    def _format_trends_for_js(self, trends):
        return [{
            'week': trend['week'].strftime('%Y-%m-%d'),
            'total': trend['total'],
            'graded': trend.get('graded', 0),
            'late': trend.get('late', 0)
        } for trend in trends]

    def _get_student_performance(self, submissions):
        return submissions.filter(
            status='graded'
        ).values(
            'student__first_name', 'student__last_name', 'student_id'
        ).annotate(
            avg_grade=Avg('grade'),
            count=Count('id'),
            late=Count('id', filter=Q(is_late=True))
        ).order_by('-avg_grade')[:10]
    
from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

# ... autres imports existants ...

class SolutionDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Solution
    template_name = 'exercises/solution_confirm_delete.html'

    def test_func(self):
        solution = self.get_object()
        return self.request.user.is_professor and solution.exercise.professor == self.request.user

    def get_success_url(self):
        return reverse('exercise-detail', kwargs={'pk': self.object.exercise.pk})

class SetDefaultSolutionView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        solution = get_object_or_404(Solution, pk=self.kwargs['pk'])
        return self.request.user.is_professor and solution.exercise.professor == self.request.user

    def post(self, request, *args, **kwargs):
        solution = get_object_or_404(Solution, pk=self.kwargs['pk'])
        Solution.objects.filter(exercise=solution.exercise).update(is_default=False)
        solution.is_default = True
        solution.save()
        return redirect('exercise-detail', pk=solution.exercise.pk)
    

# À ajouter à la fin du fichier views.py d'exercices

from django.db.models.signals import post_save
from django.dispatch import receiver
from notifications.models import Notification
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

# Hooks pour les notifications d'exercices
@receiver(post_save, sender=Exercise)
def exercise_notification(sender, instance, created, **kwargs):
    """
    Signal pour créer des notifications lorsqu'un exercice est créé ou modifié
    """
    content_type = ContentType.objects.get_for_model(instance)
    
    if created:
        # Notification pour la création d'un exercice
        Notification.objects.create_exercise_notification(
            exercise=instance,
            verb=_("Nouvel exercice disponible"),
            description=_(f"Un nouvel exercice '{instance.title}' a été publié.")
        )
    else:
        # Notification pour la modification d'un exercice
        Notification.objects.create_exercise_notification(
            exercise=instance,
            verb=_("Exercice modifié"),
            description=_(f"L'exercice '{instance.title}' a été mis à jour.")
        )

# Extension de la classe ExerciseDetailView pour inclure les notifications dans le contexte
def get_context_data_with_notifications(self, *args, **kwargs):
    """Ajoute les notifications au contexte de la vue détaillée"""
    context = original_get_context_data(self, *args, **kwargs)
    if self.request.user.is_authenticated:
        context['unread_notifications_count'] = self.request.user.notifications.unread().count()
    return context

# Sauvegarde de la méthode originale pour la restaurer plus tard
original_get_context_data = ExerciseDetailView.get_context_data
# Remplacement par notre version augmentée
ExerciseDetailView.get_context_data = get_context_data_with_notifications

    
