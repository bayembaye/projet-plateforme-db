from django.core.exceptions import ImproperlyConfigured
from security.models import EncryptionKey
from .encryption import FileEncryptor
from django.utils import timezone
from datetime import timedelta

class KeyManagementService:
    @staticmethod
    def rotate_key():
        """
        Effectue une rotation des clés de chiffrement:
        1. Génère une nouvelle clé
        2. Désactive l'ancienne clé active
        3. Enregistre la nouvelle clé
        """
        try:
            # Désactiver l'ancienne clé
            EncryptionKey.objects.filter(active=True).update(active=False)
            
            # Créer la nouvelle clé
            new_key = FileEncryptor.generate_key()
            expires_at = timezone.now() + timedelta(days=365)  # 1 an de validité
            
            EncryptionKey.objects.create(
                name=f"Auto-generated {timezone.now().date()}",
                key_material=new_key,
                version=KeyManagementService._get_next_version(),
                active=True,
                expires_at=expires_at
            )
            
            return new_key
            
        except Exception as e:
            raise ImproperlyConfigured(f"Key rotation failed: {str(e)}")

    @staticmethod
    def _get_next_version():
        last_key = EncryptionKey.objects.order_by('-version').first()
        return (last_key.version + 1) if last_key else 1

    @staticmethod
    def get_active_key():
        """Récupère la clé active actuelle"""
        key = EncryptionKey.objects.filter(active=True).first()
        if not key:
            raise ImproperlyConfigured("No active encryption key found")
        return key.key_material