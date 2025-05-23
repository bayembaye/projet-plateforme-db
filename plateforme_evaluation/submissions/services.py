import requests
import re
import logging
import tempfile
import os
import io
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError
from pypdf import PdfReader
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)

# Configuration
SECURITY_ENCRYPTION_KEY = getattr(settings, 'SECURITY_ENCRYPTION_KEY', b'default_key_here')

def extract_text_from_file(file_path):
    """Extrait le texte des fichiers PDF chiffrés"""
    try:
        with open(file_path, "rb") as f:
            encrypted_data = f.read()
        
        fernet = Fernet(SECURITY_ENCRYPTION_KEY)
        decrypted_data = fernet.decrypt(encrypted_data)
        
        with io.BytesIO(decrypted_data) as pdf_stream:
            reader = PdfReader(pdf_stream)
            extracted_text = "\n".join(page.extract_text() or "" for page in reader.pages[:10])
            # Ajout de log pour diagnostic
            logger.info(f"DIAGNOSTIC - Texte extrait du PDF: {extracted_text[:200]}...")
            return extracted_text
            
    except Exception as e:
        logger.error(f"ERREUR extraction texte: {str(e)}")
        raise ValidationError(f"Erreur lecture fichier: {str(e)}")

def generate_ai_feedback(exercise, submission_text):
    """Génère un feedback avec contraintes strictes"""
    try:
        # Prompt amélioré
        prompt = f"""
        TÂCHE: Tu es un professeur qui évalue une réponse d'étudiant à un exercice SQL. 
        Tu dois analyser la réponse et donner une note sur 20 avec un feedback structuré.
        
        IMPORTANT: Ne répète PAS la consigne. Évalue directement la réponse de l'étudiant.
        
        CONSIGNES DE L'EXERCICE:
        {exercise.title}
        {getattr(exercise, 'description', '')[:400]}
        
        RÉPONSE DE L'ÉTUDIANT À ÉVALUER:
        {submission_text[:2500]}
        
        FORMAT OBLIGATOIRE DE TA RÉPONSE (respecte exactement ce format):
        ### Note: XX/20
        
        ### Points forts:
        1. [Premier point fort]
        2. [Deuxième point fort]
        
        ### Améliorations:
        1. [Première suggestion d'amélioration]
        2. [Deuxième suggestion d'amélioration]
        
        ### Commentaire:
        [Ton analyse générale en 1-2 phrases]
        """
        
        # Log du prompt pour diagnostic
        logger.info(f"DIAGNOSTIC - Prompt envoyé à l'IA: {prompt[:200]}...")
        
        # Essayez d'abord avec un modèle plus avancé si disponible
        models_to_try = [
            "llama3", 
            "mistral", 
            "deepseek-coder:1.3b"  # Fallback au modèle original
        ]
        
        feedback = None
        for model in models_to_try:
            try:
                response = requests.post(
                    f"{settings.OLLAMA_HOST}/api/generate",
                    json={
                        "model": model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.2,
                            "repeat_penalty": 1.8
                        }
                    },
                    timeout=120
                )
                
                if response.status_code == 200:
                    feedback = response.json().get("response", "")
                    logger.info(f"DIAGNOSTIC - Réponse brute de l'IA ({model}): {feedback[:200]}...")
                    break
            except Exception as e:
                logger.warning(f"Échec avec le modèle {model}: {str(e)}")
                continue
        
        # Si aucun modèle n'a fonctionné ou si le feedback ne contient pas de note
        if not feedback or not re.search(r"^### Note:\s*\d+", feedback, re.IGNORECASE | re.MULTILINE):
            feedback = f"### Note: 10/20\n\n### Points forts:\n1. Tentative de réponse à l'exercice\n2. Format de soumission correct\n\n### Améliorations:\n1. Réponse incomplète ou incorrecte\n2. Besoin de plus de détails dans la solution\n\n### Commentaire:\nLa réponse fournie ne correspond pas complètement aux attentes de l'exercice."
        
        return feedback
            
    except Exception as e:
        logger.error(f"Erreur génération feedback: {str(e)}")
        return "### Note: 5/20\n\n### Points forts:\n1. Soumission reçue\n2. Format respecté\n\n### Améliorations:\n1. Contenu insuffisant\n2. Réponse à retravailler\n\n### Commentaire:\nErreur technique lors de l'évaluation automatique."

def extract_grade_from_feedback(feedback):
    """Extraction robuste avec garantie de résultat"""
    try:
        # Nettoyage agressif
        clean_text = re.sub(r'\s+', ' ', feedback.lower().replace(',', '.'))
        
        # 1. Recherche du format strict ### Note: XX/20
        strict_match = re.search(r"### note:\s*(\d{1,2}(?:\.\d+)?)\s*\/\s*20", clean_text)
        if strict_match:
            grade = min(20, max(0, round(float(strict_match.group(1)), 2)))
            logger.info(f"DIAGNOSTIC - Note extraite (format strict): {grade}")
            return grade

        # 2. Recherche de tout nombre/20
        any_grade = re.search(r"(\d{1,2}(?:\.\d+)?)\s*\/\s*20", clean_text)
        if any_grade:
            grade = min(20, max(0, round(float(any_grade.group(1)), 2)))
            logger.info(f"DIAGNOSTIC - Note extraite (format général): {grade}")
            return grade

        # 3. Fallback: premier nombre valide
        numbers = re.findall(r"\b\d{1,2}(?:\.\d+)?\b", clean_text)
        for num in numbers:
            grade = float(num)
            if 0 <= grade <= 20:
                logger.info(f"DIAGNOSTIC - Note extraite (premier nombre valide): {grade}")
                return round(grade, 2)

        logger.warning("DIAGNOSTIC - Aucune note extraite, utilisation de la valeur par défaut 5.0")
        return 5.0  # Valeur par défaut plus raisonnable
        
    except Exception as e:
        logger.error(f"Erreur extraction note: {str(e)}")
        return 5.0

def process_auto_correction(submission):
    """Workflow complet avec gestion d'erreur"""
    try:
        logger.info(f"Démarrage correction automatique pour soumission {submission.id}")
        # Fichier temporaire
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            for chunk in submission.file.chunks():
                tmp_file.write(chunk)
            tmp_path = tmp_file.name
        
        try:
            # Extraction texte
            text = extract_text_from_file(tmp_path)
            if not text or len(text) < 10:  # Minimum 10 caractères
                logger.warning(f"Texte extrait trop court ou vide: {text}")
                raise ValidationError("Texte non valide extrait")
            
            # Génération feedback
            feedback = generate_ai_feedback(submission.exercise, text)
            
            # Extraction note garantie
            note = extract_grade_from_feedback(feedback)
            
            # Sauvegarde
            submission.auto_feedback = feedback
            submission.auto_grade = note
            submission.grade = note  # Copie la note automatique vers le champ grade
            submission.auto_correction_date = timezone.now()
            submission.save()
            
            logger.info(f"Correction automatique réussie: note {note}/20")
            return True
            
        finally:
            if os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass
                
    except Exception as e:
        logger.error(f"ERREUR SYSTEME: {str(e)}")
        submission.auto_feedback = "Note: 5/20\n\n Points forts:\n1. Tentative de soumission\n2. Format de fichier correct\n\n### Améliorations:\n1. Erreur technique lors de l'analyse\n2. Veuillez contacter votre enseignant\n\n### Commentaire:\nUne erreur technique est survenue lors de la correction automatique."
        submission.auto_grade = 5.0
        submission.grade = 5.0  # Aussi mettre à jour le champ grade en cas d'erreur
        submission.auto_correction_date = timezone.now()
        submission.save()
        return False