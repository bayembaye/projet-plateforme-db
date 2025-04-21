from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
import logging
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings

logger = logging.getLogger(__name__)

class EncryptionError(Exception):
    pass

class FileEncryptor:
    def __init__(self, key=None):
        try:
            self.key = key or self._get_encryption_key()
            self._validate_key()
            self.cipher = Fernet(self.key)
        except Exception as e:
            logger.critical("Encryption initialization failed", exc_info=True)
            raise EncryptionError("Encryption initialization error") from e

    def _get_encryption_key(self):
        """Récupère et valide la clé depuis les settings"""
        key = getattr(settings, 'SECURITY_ENCRYPTION_KEY', None)
        if not key:
            raise ImproperlyConfigured("SECURITY_ENCRYPTION_KEY must be set in settings")
        
        # Convertir la clé en bytes si elle est en string
        if isinstance(key, str):
            key = key.encode()
        return key

    def _validate_key(self):
        """Valide le format de la clé"""
        try:
            # Vérifie que la clé peut être décodée
            decoded_key = base64.urlsafe_b64decode(self.key)
            if len(decoded_key) != 32:
                raise ValueError("Invalid key length - must be 32 bytes")
        except Exception as e:
            raise ValueError(f"Invalid key format: {str(e)}") from e

    def decrypt_file(self, input_path, output_path=None):
        """Déchiffre un fichier avec gestion robuste des erreurs"""
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"File not found: {input_path}")

        output_path = output_path or input_path + '.dec'
        temp_path = output_path + '.tmp'

        try:
            # Lecture du fichier chiffré
            with open(input_path, 'rb') as f:
                encrypted_data = f.read()
                if not encrypted_data:
                    raise EncryptionError("Empty file")

            # Déchiffrement
            decrypted_data = self.cipher.decrypt(encrypted_data)

            # Écriture du fichier temporaire
            with open(temp_path, 'wb') as f:
                f.write(decrypted_data)

            # Remplacement atomique
            os.replace(temp_path, output_path)
            return output_path

        except InvalidToken as e:
            raise EncryptionError("Invalid key or corrupted file") from e
        except Exception as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise EncryptionError(f"Decryption failed: {str(e)}") from e