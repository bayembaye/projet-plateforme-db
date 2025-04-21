
from django.core.management.base import BaseCommand
from submissions.models import Submission
from security.services.encryption import FileEncryptor
import os
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Fix encrypted files with new key'

    def handle(self, *args, **options):
        encryptor = FileEncryptor()
        
        for submission in Submission.objects.all():
            if not submission.file:
                continue
                
            file_path = submission.file.path
            if not os.path.exists(file_path):
                continue
                
            try:
                # Essai de déchiffrement
                with open(file_path, 'rb') as f:
                    try:
                        encryptor.cipher.decrypt(f.read())
                        self.stdout.write(f"OK: {submission.id}")
                        continue
                    except Exception:
                        pass
                
                # Réparation nécessaire
                self.stdout.write(f"Fixing {submission.id}...")
                
                # 1. Sauvegarde de l'original
                backup_path = file_path + '.bak'
                os.rename(file_path, backup_path)
                
                # 2. Re-chiffrement
                with open(backup_path, 'rb') as f_in:
                    with open(file_path, 'wb') as f_out:
                        f_out.write(encryptor.cipher.encrypt(f_in.read()))
                
                self.stdout.write(self.style.SUCCESS(f"Fixed {submission.id}"))
                
            except Exception as e:
                logger.error(f"Error processing {submission.id}: {str(e)}")
                self.stdout.write(self.style.ERROR(f"Failed {submission.id}"))