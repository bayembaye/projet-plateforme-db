from django.core.management.base import BaseCommand
from submissions.models import Submission
from security.services.encryption import FileEncryptor
from security.services.keys import KeyManagementService
import os
from tqdm import tqdm
from services import InvalidToken

class Command(BaseCommand):
    help = 'Encrypt all existing submission files with the current active key'

    def handle(self, *args, **options):
        # Vérifier qu'une clé active existe
        try:
            active_key = KeyManagementService.get_active_key()
            self.stdout.write(f"Using active encryption key: {active_key[:10]}...")
        except Exception as e:
            self.stdout.write(self.style.ERROR(str(e)))
            return

        encryptor = FileEncryptor()
        submissions = Submission.objects.exclude(file='')
        
        self.stdout.write(f"Found {submissions.count()} submissions to process...")
        
        success = skipped = errors = 0
        
        for sub in tqdm(submissions, desc="Processing submissions"):
            if not hasattr(sub.file, 'path') or not os.path.exists(sub.file.path):
                skipped += 1
                continue
                
            try:
                # Vérifie si déjà chiffré
                with open(sub.file.path, 'rb') as f:
                    header = f.read(100)
                    try:
                        encryptor.cipher.decrypt(header)  # Test de déchiffrement
                        skipped += 1
                        continue
                    except InvalidToken:
                        pass  # Le fichier n'est pas chiffré
                
                # Chiffre le fichier
                encryptor.encrypt_file(sub.file.path)
                success += 1
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error processing {sub.id}: {str(e)}"))
                errors += 1
                
        self.stdout.write(self.style.SUCCESS(
            f"Process complete: {success} encrypted, {skipped} already encrypted/skipped, {errors} errors"
        ))