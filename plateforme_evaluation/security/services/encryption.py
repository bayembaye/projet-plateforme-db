import base64
import logging
import os
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from security.models import SecurityEvent, EncryptionKey
from django.utils import timezone

logger = logging.getLogger(__name__)

class EncryptionError(Exception):
    """Exception personnalisée pour les erreurs de chiffrement"""
    pass

class FileEncryptor:
    def __init__(self, key=None):
        """
        Initialise le service de chiffrement avec journalisation des événements.
        :param key: Clé personnalisée (optionnelle)
        """
        try:
            self.key = key or self._get_active_encryption_key()
            self._validate_key()
            self.cipher = Fernet(self.key)
        except Exception as e:
            self._log_security_event('KEY_MGMT', 'Initialization failed', error=str(e))
            logger.critical("Échec d'initialisation du service de chiffrement", exc_info=True)
            raise EncryptionError("Erreur d'initialisation du chiffrement") from e

    def _get_active_encryption_key(self):
        """Récupère la clé active depuis la base de données ou les settings"""
        try:
            active_key = EncryptionKey.objects.filter(active=True).first()
            if active_key:
                return active_key.key_material
            
            # Fallback aux settings si aucune clé en base
            key = getattr(settings, 'SECURITY_ENCRYPTION_KEY', None)
            if not key:
                raise ImproperlyConfigured("Aucune clé de chiffrement configurée")
                
            if isinstance(key, str):
                key = key.encode()
                
            return key
            
        except Exception as e:
            logger.error("Erreur lors de la récupération de la clé", exc_info=True)
            raise

    def _validate_key(self):
        """Valide que la clé a le bon format"""
        try:
            decoded_key = base64.urlsafe_b64decode(self.key)
            if len(decoded_key) != 32:
                raise ValueError("Clé invalide - doit décoder en 32 bytes")
        except Exception as e:
            self._log_security_event('KEY_MGMT', 'Invalid key format', error=str(e))
            raise ValueError("Clé de chiffrement mal formée") from e

    def encrypt_file(self, input_path, output_path=None):
        """
        Chiffre un fichier de manière sécurisée avec journalisation.
        Si output_path n'est pas spécifié, remplace le fichier original.
        """
        try:
            output_path = output_path or input_path
            temp_path = output_path + '.tmp'

            # Vérification des chemins
            if not os.path.exists(input_path):
                raise FileNotFoundError(f"Fichier source introuvable: {input_path}")

            # Lecture et chiffrement
            with open(input_path, 'rb') as f:
                encrypted_data = self.cipher.encrypt(f.read())

            # Écriture sécurisée
            with open(temp_path, 'wb') as f:
                f.write(encrypted_data)

            # Remplacement atomique
            if output_path == input_path:
                os.replace(temp_path, output_path)
            else:
                os.rename(temp_path, output_path)

            self._log_security_event(
                'FILE_OP',
                f'File encrypted: {input_path} -> {output_path}',
                file_size=os.path.getsize(output_path)
            )
            return True

        except Exception as e:
            self._log_security_event(
                'FILE_OP',
                f'Encryption failed: {input_path}',
                error=str(e),
                status='failed'
            )
            # Nettoyage en cas d'erreur
            if 'temp_path' in locals() and os.path.exists(temp_path):
                os.remove(temp_path)
            raise EncryptionError(f"Échec du chiffrement: {str(e)}") from e

    def decrypt_file(self, input_path, output_path=None):
        """
        Déchiffre un fichier avec gestion des erreurs et journalisation.
        Si output_path n'est pas spécifié, crée un fichier temporaire.
        """
        try:
            if not os.path.exists(input_path):
                raise FileNotFoundError(f"Fichier chiffré introuvable: {input_path}")

            output_path = output_path or input_path + '.dec'
            temp_path = output_path + '.tmp'

            # Lecture et déchiffrement
            with open(input_path, 'rb') as f:
                decrypted_data = self.cipher.decrypt(f.read())

            # Écriture sécurisée
            with open(temp_path, 'wb') as f:
                f.write(decrypted_data)

            os.replace(temp_path, output_path)

            self._log_security_event(
                'FILE_OP',
                f'File decrypted: {input_path} -> {output_path}',
                status='success'
            )
            return output_path

        except InvalidToken as e:
            self._log_security_event(
                'FILE_OP',
                f'Invalid token for: {input_path}',
                error='Invalid token or key',
                status='failed'
            )
            raise EncryptionError("Clé de déchiffrement invalide ou fichier corrompu") from e
        except Exception as e:
            self._log_security_event(
                'FILE_OP',
                f'Decryption failed: {input_path}',
                error=str(e),
                status='failed'
            )
            if 'temp_path' in locals() and os.path.exists(temp_path):
                os.remove(temp_path)
            raise EncryptionError(f"Échec du déchiffrement: {str(e)}") from e

    def _log_security_event(self, event_type, action, **details):
        """Journalise un événement de sécurité"""
        try:
            SecurityEvent.objects.create(
                event_type=event_type,
                details={
                    'action': action,
                    'timestamp': timezone.now().isoformat(),
                    **details
                }
            )
        except Exception as e:
            logger.error(f"Failed to log security event: {str(e)}", exc_info=True)

    @staticmethod
    def generate_key():
        """Génère une nouvelle clé de chiffrement valide"""
        return Fernet.generate_key()