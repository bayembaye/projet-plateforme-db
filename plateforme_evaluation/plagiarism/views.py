import logging
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseForbidden, JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import permission_required
from django.urls import reverse
from django.utils import timezone
from django.contrib import messages
from submissions.models import Submission
from .models import PlagiarismScan
from .services import PlagiarismDetector

logger = logging.getLogger(__name__)

class PlagiarismScanListView(LoginRequiredMixin, ListView):
    model = PlagiarismScan
    template_name = 'plagiarism/scan_list.html'
    context_object_name = 'scans'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_professor:
            queryset = queryset.filter(submission__student=self.request.user)
        return queryset.select_related('submission', 'submission__exercise')

class PlagiarismScanDetailView(LoginRequiredMixin, DetailView):
    model = PlagiarismScan
    template_name = 'plagiarism/scan_detail.html'
    context_object_name = 'scan'

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_professor:
            queryset = queryset.filter(submission__student=self.request.user)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['timezone_now'] = timezone.now()
        return context

@permission_required('plagiarism.can_start_scan')
def start_plagiarism_scan(request, submission_id):
    """Vue pour lancer un scan de plagiat avec redirection"""
    submission = get_object_or_404(Submission, pk=submission_id)
    
    if not request.user.is_professor:
        return HttpResponseForbidden("Seuls les professeurs peuvent lancer des scans")
    
    detector = PlagiarismDetector()
    scan = PlagiarismScan.objects.create(
        submission=submission,
        scan_type=request.GET.get('scan_type', 'BOTH'),
        status='PROCESSING'
    )

    try:
        results = detector.scan_submission(submission)
        scan.result_data = results
        scan.similarity_score = results.get('overall_similarity', 0)
        scan.status = 'COMPLETED'
        scan.completed_at = timezone.now()
        scan.save()
        
        messages.success(request, "Scan terminé avec succès!")
        return redirect('plagiarism:scan-detail', pk=scan.id)
        
    except Exception as e:
        scan.status = 'FAILED'
        scan.error_message = str(e)
        scan.completed_at = timezone.now()
        scan.save()
        logger.error(f"Échec scan {scan.id}: {str(e)}", exc_info=True)
        messages.error(request, f"Échec du scan: {str(e)}")
        return redirect('plagiarism:scan-detail', pk=scan.id)

@require_POST
@permission_required('plagiarism.can_start_scan')
def start_plagiarism_scan_api(request, submission_id):
    """Version API pour les requêtes AJAX"""
    try:
        submission = get_object_or_404(Submission, pk=submission_id)
        detector = PlagiarismDetector()

        scan = PlagiarismScan.objects.create(
            submission=submission,
            scan_type=request.POST.get('scan_type', 'INTERNAL'),
            status='PROCESSING'
        )

        try:
            results = detector.scan_submission(submission)
            scan.result_data = results
            scan.similarity_score = results.get('overall_similarity', 0)
            scan.status = 'COMPLETED'
            scan.completed_at = timezone.now()
            scan.save()

            return JsonResponse({
                'status': 'success',
                'scan_id': str(scan.id),
                'redirect_url': reverse('plagiarism:scan-detail', kwargs={'pk': scan.id})
            })

        except Exception as e:
            scan.status = 'FAILED'
            scan.error_message = str(e)
            scan.completed_at = timezone.now()
            scan.save()
            logger.error(f"Échec scan {scan.id}: {str(e)}", exc_info=True)
            return JsonResponse({
                'status': 'error',
                'error': str(e),
                'scan_id': str(scan.id)
            }, status=500)

    except Exception as e:
        logger.error(f"Erreur initiale scan: {str(e)}", exc_info=True)
        return JsonResponse({
            'status': 'error',
            'error': str(e)
        }, status=400)