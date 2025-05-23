from django.db.models.signals import post_save
from django.dispatch import receiver
from submissions.models import Submission
from .models import PlagiarismScan
from django.conf import settings

@receiver(post_save, sender=Submission)
def auto_plagiarism_scan(sender, instance, created, **kwargs):
    if created and instance.status == instance.Status.SUBMITTED:
        if getattr(settings, 'AUTO_PLAGIARISM_SCAN', False):
            scan = PlagiarismScan.objects.create(
                submission=instance,
                scan_type='INTERNAL'
            )
            scan.start_scan()