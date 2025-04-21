import os
from django.core.management.base import BaseCommand
from django.conf import settings
from submissions.models import Submission
from plagiarism.models import DocumentFingerprint
from security.services.encryption import FileEncryptor
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Reset encryption system and regenerate fingerprints'

    def handle(self, *args, **options):
        # 1. Generate new encryption key
        new_key = FileEncryptor.generate_key()
        self.stdout.write(self.style.SUCCESS(f'New encryption key: {new_key.decode()}'))
        self.stdout.write(self.style.WARNING('Add this to your settings.py:\n'))
        self.stdout.write(f'SECURITY_ENCRYPTION_KEY = {new_key}\n')

        # 2. Re-encrypt all submission files
        encryptor = FileEncryptor(new_key)
        submissions = Submission.objects.all()
        
        self.stdout.write('Re-encrypting submission files...')
        for sub in submissions:
            try:
                if sub.file:
                    original_path = sub.file.path
                    temp_path = original_path + '.tmp'
                    
                    # Decrypt (with old key if possible)
                    try:
                        with open(original_path, 'rb') as f:
                            content = f.read()
                    except Exception as e:
                        logger.error(f"Error reading {original_path}: {str(e)}")
                        continue
                    
                    # Encrypt with new key
                    try:
                        encrypted = encryptor.cipher.encrypt(content)
                        with open(temp_path, 'wb') as f:
                            f.write(encrypted)
                        os.replace(temp_path, original_path)
                        self.stdout.write(f'Success: {sub.id}')
                    except Exception as e:
                        logger.error(f"Encryption failed for {sub.id}: {str(e)}")
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
            except Exception as e:
                logger.error(f"Error processing {sub.id}: {str(e)}")

        # 3. Clear and regenerate fingerprints
        self.stdout.write('Regenerating fingerprints...')
        DocumentFingerprint.objects.all().delete()
        
        from plagiarism.services.detector import PlagiarismDetector
        detector = PlagiarismDetector()
        detector._initialize_fingerprints()  # Force regeneration
        
        self.stdout.write(self.style.SUCCESS('Encryption reset completed!'))