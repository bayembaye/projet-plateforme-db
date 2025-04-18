# accounts/management/commands/generate_stats.py (nouveau fichier)

from django.core.management.base import BaseCommand
from accounts.models import StudentPerformance, User
from submissions.models import Submission
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Génère les statistiques de performance pour tous les étudiants'

    def handle(self, *args, **options):
        for student in User.objects.filter(role='STUDENT'):
            submissions = Submission.objects.filter(
                student=student,
                status='graded'
            ).select_related('exercise')
            
            if submissions.count() >= 3:  # Seulement si l'étudiant a au moins 3 soumissions
                # Calcul des stats
                student_avg = submissions.aggregate(avg=Avg('grade'))['avg']
                class_avg = Submission.objects.filter(
                    exercise__in=submissions.values('exercise')
                ).exclude(student=student).aggregate(avg=Avg('grade'))['avg'] or 0
                
                # Calcul par catégorie
                category_stats = submissions.values(
                    'exercise__category__name'
                ).annotate(
                    avg_grade=Avg('grade'),
                    count=Count('id')
                ).order_by('-avg_grade')
                
                # Crée un enregistrement de performance
                StudentPerformance.objects.create(
                    student=student,
                    average_score=student_avg,
                    class_average=class_avg,
                    improvement_rate=self._calculate_improvement(student),
                    category_breakdown={item['exercise__category__name']: item['avg_grade'] 
                                      for item in category_stats},
                    submission_count=submissions.count(),
                    late_submissions=submissions.filter(is_late=True).count()
                )
                
                self.stdout.write(f'Stats générées pour {student.email}')

    def _calculate_improvement(self, student):
        """Calcule le taux d'amélioration sur les 3 derniers mois."""
        time_period = timezone.now() - timedelta(days=90)
        midpoint = timezone.now() - timedelta(days=45)
        
        # Première moitié de la période
        first_half = Submission.objects.filter(
            student=student,
            status='graded',
            submission_date__gte=time_period,
            submission_date__lt=midpoint
        ).aggregate(avg=Avg('grade'))['avg'] or 0
        
        # Deuxième moitié de la période
        second_half = Submission.objects.filter(
            student=student,
            status='graded',
            submission_date__gte=midpoint
        ).aggregate(avg=Avg('grade'))['avg'] or 0
        
        if first_half > 0:
            return ((second_half - first_half) / first_half) * 100
        return 0