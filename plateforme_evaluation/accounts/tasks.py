from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.db.models import Avg, Count
from accounts.models import StudentPerformance, User
from submissions.models import Submission

@shared_task
def record_student_performance():
    students = User.objects.filter(is_student=True)
    for student in students:
        try:
            # Calcul sur les 30 derniers jours
            time_period = 30
            end_date = timezone.now()
            start_date = end_date - timedelta(days=time_period)
            
            submissions = Submission.objects.filter(
                student=student,
                status='graded',
                grade__isnull=False,
                submission_date__range=(start_date, end_date)
            )
            
            if submissions.exists():
                # Calcul des moyennes
                student_avg = submissions.aggregate(avg=Avg('grade'))['avg']
                exercise_ids = submissions.values_list('exercise_id', flat=True)
                class_avg = Submission.objects.filter(
                    exercise_id__in=exercise_ids
                ).exclude(student=student).aggregate(avg=Avg('grade'))['avg'] or 0
                
                # Stats par catégorie
                categories = submissions.values(
                    'exercise__category__name'
                ).annotate(
                    student_avg=Avg('grade'),
                    count=Count('id')
                )
                
                category_breakdown = {
                    cat['exercise__category__name']: {
                        'student_avg': cat['student_avg'],
                        'count': cat['count']
                    }
                    for cat in categories
                }
                
                # Enregistrement
                StudentPerformance.objects.create(
                    student=student,
                    average_score=student_avg,
                    class_average=class_avg,
                    submission_count=submissions.count(),
                    late_submissions=submissions.filter(is_late=True).count(),
                    category_breakdown=category_breakdown
                )
        except Exception as e:
            print(f"Erreur pour l'étudiant {student.id}: {str(e)}")