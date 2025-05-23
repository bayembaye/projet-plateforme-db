from django.core.management.base import BaseCommand
from plagiarism.services.detector import PlagiarismDetector

class Command(BaseCommand):
    help = 'Initialize plagiarism detection fingerprints'

    def handle(self, *args, **options):
        detector = PlagiarismDetector()
        self.stdout.write(self.style.SUCCESS('Système de détection initialisé'))