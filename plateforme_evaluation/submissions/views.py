from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    UpdateView,
    DeleteView
)
from django.contrib.auth.mixins import (
    LoginRequiredMixin, 
    UserPassesTestMixin
)
from django.urls import reverse, reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseForbidden
from .services import extract_text_from_file, generate_ai_feedback, process_auto_correction
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import Submission
from .forms import SubmissionForm
from exercises.models import Exercise
from accounts.models import User
import uuid
from django.db.models import Avg  
from exercises.models import Exercise  
from submissions.models import Submission  

from django.db import transaction
from django.db.utils import IntegrityError
import uuid

class SubmissionCreateView(LoginRequiredMixin, CreateView):
    model = Submission
    form_class = SubmissionForm

    @transaction.atomic
    def form_valid(self, form):
        form.instance.exercise = get_object_or_404(Exercise, pk=self.kwargs['exercise_id'])
        form.instance.student = self.request.user
        
        try:
            # Force un UUID valide si nécessaire
            if not form.instance.id:
                form.instance.id = uuid.uuid4()
            
            submission = form.save(commit=False)
            submission.submit()  # Transition FSM
            
            # Sauvegarde explicite avec force_insert
            submission.save(force_insert=True)
            
            # Notification
            Notification.objects.create_user_notification(
                user=submission.exercise.professor,
                verb="Nouvelle soumission",
                description=f"Nouvelle soumission pour {submission.exercise.title}",
                target=submission
            )
            
            messages.success(self.request, "Soumission réussie!")
            return redirect('submission-detail', pk=submission.pk)
            
        except IntegrityError as e:
            if 'too large' in str(e):
                # Régénère un UUID si problème de taille
                form.instance.id = uuid.uuid4()
                return self.form_valid(form)  # Réessaye
            messages.error(self.request, f"Erreur d'intégrité: {str(e)}")
            return self.form_invalid(form)
            
       
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['exercise_id'] = self.kwargs['exercise_id']  # Ajoutez ceci
        return context    
from django.db.models import Avg, Count
from django.utils import timezone

class SubmissionListView(LoginRequiredMixin, ListView):
    model = Submission
    template_name = 'submissions/submission_list.html'
    context_object_name = 'submissions'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        
        if self.request.user.is_professor:
            queryset = queryset.filter(exercise__professor=self.request.user)
        else:
            queryset = queryset.filter(student=self.request.user)
            
        exercise_id = self.request.GET.get('exercise')
        if exercise_id:
            queryset = queryset.filter(exercise_id=exercise_id)
            
        return queryset.select_related('student', 'exercise', 'exercise__category')\
                      .order_by('-submission_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_professor'] = self.request.user.is_professor
        context['timezone_now'] = timezone.now()
        
        if not self.request.user.is_professor:
            # Statistiques pour les étudiants
            submissions = self.get_queryset()
            graded_submissions = submissions.filter(status='graded')
            
            context['total_exercises'] = Exercise.objects.filter(is_active=True).count()
            context['submitted_exercises'] = submissions.values('exercise').distinct().count()
            context['pending_exercises'] = context['total_exercises'] - context['submitted_exercises']
            
            # Moyenne générale
            if graded_submissions.exists():
                context['average_grade'] = graded_submissions.aggregate(
                    avg_grade=Avg('grade')
                )['avg_grade']
            
            # Performance par catégorie
            context['category_stats'] = graded_submissions.values(
                'exercise__category__name'
            ).annotate(
                average_grade=Avg('grade'),
                count=Count('id')
            ).order_by('exercise__category__name')
            
            # Répartition des feedbacks
            context['feedback_distribution'] = {
                'Excellent': graded_submissions.filter(feedback__icontains='excellent').count(),
                'Très_bien': graded_submissions.filter(feedback__icontains='très bien').count(),
                'Bien': graded_submissions.filter(feedback__icontains='bien').count(),
                'Passable': graded_submissions.filter(feedback__icontains='passable').count(),
                'Insuffisant': graded_submissions.filter(feedback__icontains='insuffisant').count(),
            }
        
        return context

class SubmissionDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Submission
    template_name = 'submissions/submission_detail.html'

    def test_func(self):
        submission = self.get_object()
        return (
            submission.student == self.request.user or  # L'étudiant peut voir
            (self.request.user.is_professor and  # Ou le professeur propriétaire
             submission.exercise.professor == self.request.user)
        )
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        submission = self.object
        
        context['can_edit'] = (
            not self.request.user.is_professor and
            submission.status == Submission.Status.DRAFT
        )
        
        context['can_dispute'] = (
            not self.request.user.is_professor and
            submission.status == Submission.Status.GRADED and
            not submission.is_disputed
        )
        
        context['can_grade'] = (
            self.request.user.is_professor and
            submission.status in [Submission.Status.SUBMITTED, Submission.Status.UNDER_REVIEW]
        )
        
        context['can_resolve_dispute'] = (
            self.request.user.is_professor and
            submission.is_disputed and
            submission.status == Submission.Status.GRADED
        )
        
        context['timezone_now'] = timezone.now()
        return context

from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse
from django.utils import timezone
from django.contrib import messages
from .models import Submission
from .forms import SubmissionForm

class SubmissionUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Submission
    form_class = SubmissionForm
    template_name = 'submissions/submission_form.html'

    def test_func(self):
        """Vérifie que l'utilisateur peut modifier cette soumission."""
        submission = self.get_object()
        return (
            submission.student == self.request.user and  # Seul l'étudiant propriétaire
            (
                submission.status == Submission.Status.DRAFT or  # Peut modifier les brouillons
                (
                    submission.status == Submission.Status.SUBMITTED and
                    submission.exercise.deadline and
                    submission.exercise.deadline > timezone.now()  # Peut modifier si deadline pas dépassée
                )
            )
        )

    def get_success_url(self):
        """Redirige vers la page de détail de la soumission après modification."""
        messages.success(self.request, "Soumission mise à jour avec succès !")
        return reverse('submission-detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['exercise'] = self.object.exercise  # Assure que exercise est toujours dans le contexte
        context['timezone_now'] = timezone.now()
        context['can_edit'] = (
            self.object.status == Submission.Status.DRAFT or
            (self.object.exercise.deadline and self.object.exercise.deadline > timezone.now())
        )
        return context


    def form_valid(self, form):
        """Logique supplémentaire après validation du formulaire."""
        # Exemple : Logique de mise à jour personnalisée
        if self.object.status == Submission.Status.DRAFT and 'submit' in self.request.POST:
            try:
                self.object.submit()  # Transition FSM vers "SUBMITTED"
            except ValidationError as e:
                messages.error(self.request, str(e))
                return self.form_invalid(form)

        return super().form_valid(form)
class SubmissionDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Submission
    template_name = 'submissions/submission_confirm_delete.html'
    success_url = reverse_lazy('submission-list')

    def test_func(self):
        submission = self.get_object()
        if self.request.user.is_professor:
            return submission.exercise.professor == self.request.user
        return submission.student == self.request.user

    def delete(self, request, *args, **kwargs):
        messages.success(request, _("Soumission supprimée avec succès."))
        return super().delete(request, *args, **kwargs)

from django import forms
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic.edit import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.validators import MinValueValidator, MaxValueValidator
from .models import Submission

class GradeSubmissionForm(forms.ModelForm):
    grade = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(20)],
        widget=forms.NumberInput(attrs={
            'step': '0.01',
            'min': '0',
            'max': '20',
            'class': 'form-control'
        })
    )

    class Meta:
        model = Submission
        fields = ['grade', 'feedback']

class GradeSubmissionView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Submission
    form_class = GradeSubmissionForm
    template_name = 'submissions/grade_submission.html'

    def test_func(self):
        submission = self.get_object()
        return (
            self.request.user.is_professor and
            submission.exercise.professor == self.request.user and
            submission.status in [Submission.Status.SUBMITTED, Submission.Status.UNDER_REVIEW]
        )

    def form_valid(self, form):
        submission = form.save(commit=False)
        
        try:
            # Conversion explicite pour éviter les erreurs de type
            grade = float(form.cleaned_data['grade'])
            
            # Transition vers UNDER_REVIEW si nécessaire
            if submission.status == Submission.Status.SUBMITTED:
                submission.assign_for_review()
            
            # Appliquer la note
            submission.grade_submission(
                grade=grade,
                feedback=form.cleaned_data['feedback']
            )
            submission.save()
            
            messages.success(self.request, "La note a été enregistrée avec succès !")
            return redirect(self.get_success_url())
            
        except (ValueError, TypeError) as e:
            messages.error(self.request, f"Erreur : La note doit être un nombre valide.")
            return self.form_invalid(form)
        except ValidationError as e:
            messages.error(self.request, f"Erreur : {e}")
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse('submission-detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['submission'] = self.object
        return context
    

    def get_initial(self):
        initial = super().get_initial()
        submission = self.get_object()
        
        # Pré-remplir avec la correction automatique si disponible
        if submission.auto_grade and not submission.grade:
            initial['grade'] = submission.auto_grade
        if submission.auto_feedback and not submission.feedback:
            initial['feedback'] = submission.auto_feedback
            
        return initial
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['submission'] = self.object
        context['auto_correction_available'] = (
            self.object.auto_feedback and 
            not self.object.feedback and
            not self.object.grade
        )
        return context

class DisputeSubmissionView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Submission
    fields = ['dispute_reason']
    template_name = 'submissions/dispute_submission.html'
    
    def test_func(self):
        submission = self.get_object()
        return (
            not self.request.user.is_professor and
            submission.student == self.request.user and
            submission.status == Submission.Status.GRADED and
            not submission.is_disputed
        )
    
    def form_valid(self, form):
        submission = form.save(commit=False)
        reason = form.cleaned_data.get('dispute_reason', '')  # Récupère la raison
        
        if not reason:
            form.add_error('dispute_reason', "Une raison est requise")
            return self.form_invalid(form)
            
        try:
            submission.dispute(reason=reason)  # Passez la raison ici
            submission.save()
            messages.success(self.request, _("Contestation envoyée avec succès."))
            return redirect(self.get_success_url())
        except ValidationError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)
    
    def get_success_url(self):
        return reverse('submission-detail', kwargs={'pk': self.object.pk})
    
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse
from .services import process_auto_correction
import time

class AutoCorrectSubmissionView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        submission = self.get_object()
        return (
            self.request.user.is_professor and
            submission.exercise.professor == self.request.user and
            submission.status in [Submission.Status.SUBMITTED, Submission.Status.UNDER_REVIEW]
        )
    
    def get_object(self):
        return get_object_or_404(Submission, pk=self.kwargs['pk'])
    
    def post(self, request, *args, **kwargs):
        submission = self.get_object()
        
        # Délai minimal pour éviter les appels trop rapides
        time.sleep(1)
        
        success = process_auto_correction(submission)
        
        if success:
            return JsonResponse({
                'status': 'success',
                'auto_feedback': submission.auto_feedback,
                'auto_grade': str(submission.auto_grade) if submission.auto_grade else None
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Erreur lors de la correction automatique'
            }, status=400)    
    # Dans views.py
from django.core.exceptions import ValidationError
from django.http import JsonResponse
import tempfile
import os

def auto_correct_submission(request, submission_id):
    submission = get_object_or_404(Submission, pk=submission_id)
    
    try:
        # Crée un fichier temporaire avec la bonne extension
        with tempfile.NamedTemporaryFile(
            suffix=os.path.splitext(submission.file.name)[1], 
            delete=False
        ) as tmp:
            for chunk in submission.file.chunks():
                tmp.write(chunk)
            file_path = tmp.name

        try:
            # Extraction et correction
            extracted_text = extract_text_from_file(file_path)
            feedback = generate_ai_feedback(submission.exercise, extracted_text)
            
            # Sauvegarde
            submission.auto_feedback = feedback
            submission.save()
            
            return JsonResponse({
                'status': 'success',
                'feedback': feedback
            })
            
        finally:
            os.unlink(file_path)  # Nettoyage
            
    except ValidationError as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f"Erreur interne: {str(e)}"
        }, status=500)   


# À ajouter au fichier views.py des soumissions

from django.db.models.signals import post_save
from django.dispatch import receiver
from notifications.models import Notification
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

@receiver(post_save, sender=Submission)
def submission_notification(sender, instance, created, **kwargs):
    """
    Signal pour créer des notifications lorsqu'une soumission est créée ou modifiée
    """
    content_type = ContentType.objects.get_for_model(instance)
    
    if created:
        # Notification au professeur pour une nouvelle soumission
        if instance.exercise.professor:
            Notification.objects.create_user_notification(
                user=instance.exercise.professor,
                verb=_("Nouvelle soumission"),
                description=_(f"Un étudiant a soumis un travail pour l'exercice '{instance.exercise.title}'"),
                target=instance
            )
    else:
        # Notification à l'étudiant si la soumission est notée
        if instance.status == 'graded' and instance.student:
            Notification.objects.create_user_notification(
                user=instance.student,
                verb=_("Soumission notée"),
                description=_(f"Votre soumission pour l'exercice '{instance.exercise.title}' a été notée. Note: {instance.grade}/20"),
                target=instance
            )
        
        # Notification au professeur si la soumission est contestée
        if instance.status == 'disputed' and instance.exercise.professor:
            Notification.objects.create_user_notification(
                user=instance.exercise.professor,
                verb=_("Contestation de note"),
                description=_(f"Un étudiant conteste sa note pour l'exercice '{instance.exercise.title}'"),
                target=instance
            )     
    

