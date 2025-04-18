from django.core.management.base import BaseCommand
from security.services.keys import KeyManagementService
from security.models import EncryptionKey

class Command(BaseCommand):
    help = 'Effectue une rotation des clés de chiffrement'
    
    def handle(self, *args, **options):
        new_key = KeyManagementService.rotate_key()
        self.stdout.write(self.style.SUCCESS(f'Clé rotée avec succès: {new_key[:10]}...'))