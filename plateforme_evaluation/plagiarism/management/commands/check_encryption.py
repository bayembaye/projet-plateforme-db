from django.core.management.base import BaseCommand
from submissions.models import Submission
from security.services.encryption import FileEncryptor
import magic  # pip install python-magic-bin sur Windows

class Command(BaseCommand):
    help = 'Verify file encryption status'

    def handle(self, *args, **options):
        encryptor = FileEncryptor()
        mime = magic.Magic(mime=True)

        for sub in Submission.objects.all():
            if not sub.file:
                continue

            try:
                # Vérifier le type MIME
                file_type = mime.from_file(sub.file.path)
                
                # Essayer de déchiffrer
                with open(sub.file.path, 'rb') as f:
                    data = f.read(100)  # Lire juste les premiers bytes
                    try:
                        encryptor.cipher.decrypt(data)
                        status = "ENCRYPTED"
                    except:
                        status = "PLAINTEXT"
                
                self.stdout.write(f"{sub.id} - {file_type} - {status}")
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error checking {sub.id}: {str(e)}"))