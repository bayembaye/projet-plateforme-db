import os
import logging
import tempfile
from django.core.exceptions import ValidationError
from security.services.encryption import FileEncryptor
from cryptography.fernet import InvalidToken

logger = logging.getLogger(__name__)

class FileProcessor:
    """Solution complète avec journalisation détaillée"""

    SUPPORTED_EXTENSIONS = ['.pdf', '.docx', '.doc', '.txt']

    @staticmethod
    def extract_text_from_bytes(file_bytes, original_filename):
        """
        Extrait le texte avec une journalisation complète
        """
        logger.info(f"Début extraction - Taille fichier: {len(file_bytes)} bytes, Nom: '{original_filename}'")

        try:
            # Validation initiale renforcée
            if not file_bytes:
                logger.error("Erreur: Aucun contenu fourni")
                raise ValidationError("Aucun contenu fourni")
            
            if not original_filename:
                logger.error("Erreur: Nom de fichier vide")
                raise ValidationError("Nom de fichier vide")

            filename = original_filename.strip()
            logger.debug(f"Nom fichier nettoyé: '{filename}'")

            if '.' not in filename:
                logger.error(f"Erreur: Pas d'extension dans le nom '{filename}'")
                raise ValidationError("Le fichier n'a pas d'extension")

            extension = os.path.splitext(filename)[1].lower()
            logger.debug(f"Extension détectée: '{extension}'")

            if not extension:
                logger.error("Erreur: Extension vide après split")
                raise ValidationError("Extension de fichier vide")

            if extension not in FileProcessor.SUPPORTED_EXTENSIONS:
                logger.error(f"Erreur: Extension non supportée: '{extension}'")
                raise ValidationError(
                    f"Format non supporté: '{extension}'. "
                    f"Formats acceptés: {', '.join(FileProcessor.SUPPORTED_EXTENSIONS)}"
                )

            # Création fichier temporaire
            with tempfile.NamedTemporaryFile(suffix=extension, delete=False) as tmp_file:
                tmp_path = tmp_file.name
                tmp_file.write(file_bytes)
                logger.debug(f"Fichier temporaire créé: {tmp_path} ({os.path.getsize(tmp_path)} bytes)")

            try:
                logger.info(f"Tentative d'extraction pour {extension}")
                
                if extension == '.pdf':
                    text = FileProcessor._extract_pdf(tmp_path)
                elif extension in ['.docx', '.doc']:
                    text = FileProcessor._extract_word(tmp_path)
                else:  # .txt
                    text = FileProcessor._extract_text(tmp_path)

                logger.info(f"Extraction réussie - {len(text)} caractères")
                return text

            finally:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
                    logger.debug("Fichier temporaire supprimé")
                    
        except ValidationError as ve:
            logger.error(f"VALIDATION ERROR: {str(ve)}")
            raise
        except Exception as e:
            logger.error(f"ERREUR TECHNIQUE: {str(e)}", exc_info=True)
            raise ValidationError(f"Erreur technique lors du traitement du fichier")

import PyPDF2
from io import BytesIO
import logging
import magic
from django.core.exceptions import ValidationError
import os

# Gestion des imports PDFMiner
try:
    from pdfminer.high_level import extract_text
except ImportError:
    try:
        from pdfminer3k.high_level import extract_text
    except ImportError as e:
        raise ImportError(
            "PDFMiner non installé. Utilisez : "
            "pip install pdfminer.six"
        ) from e

logger = logging.getLogger(__name__)

class FileProcessor:
    @staticmethod
    def extract_text_from_bytes(content, filename):
        """Version robuste avec vérification de chiffrement"""
        try:
            # Vérification du chiffrement
            try:
                encryptor = FileEncryptor()
                content = encryptor.cipher.decrypt(content)
            except InvalidToken:
                pass  # Non chiffré

            # Extraction selon le type
            file_type = magic.from_buffer(content[:1024], mime=True)
            if 'pdf' in file_type:
                return FileProcessor._extract_pdf(BytesIO(content))
            # ... autres types
        except Exception as e:
            logger.error(f"Échec extraction: {str(e)}", exc_info=True)
            raise ValidationError(f"Erreur traitement fichier: {str(e)}")
    @staticmethod
    def _extract_pdf(content):
        """Extrait le texte d'un PDF avec trois méthodes de fallback"""
        text = ""
        
        # Méthode 1: PyPDF2 (rapide)
        try:
            with BytesIO(content) as pdf_file:
                reader = PyPDF2.PdfReader(pdf_file)
                if reader.is_encrypted:
                    raise ValidationError("PDF protégé par mot de passe")
                
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            
            if text.strip():
                return text
        except Exception as e:
            logger.warning(f"PyPDF2 échoué: {str(e)}")

        # Méthode 2: pdfminer (robuste)
        try:
            text = extract_text(BytesIO(content))
            if text.strip():
                return text
            raise ValidationError("PDF vide ou texte non extractible")
        except Exception as e:
            logger.error(f"pdfminer échoué: {str(e)}")
            raise ValidationError("Échec de l'extraction du texte PDF")
    @staticmethod
    def _extract_word(file_path):
        """Extraction Word avec logs"""
        logger.debug(f"Début extraction Word: {file_path}")
        try:
            import docx
            doc = docx.Document(file_path)
            paragraphs = [p.text for p in doc.paragraphs if p.text]
            logger.debug(f"DOCX détecté - {len(paragraphs)} paragraphes")
            return "\n".join(paragraphs)
        except Exception as e:
            logger.error(f"ERREUR WORD: {str(e)}", exc_info=True)
            raise ValidationError(f"Erreur lecture Word: {str(e)}")

    @staticmethod
    def _extract_text(file_path):
        """Extraction texte avec logs"""
        logger.debug(f"Début extraction texte: {file_path}")
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                logger.debug(f"TXT détecté - {len(content)} caractères")
                return content
        except Exception as e:
            logger.error(f"ERREUR TXT: {str(e)}", exc_info=True)
            raise ValidationError(f"Erreur lecture fichier texte: {str(e)}")