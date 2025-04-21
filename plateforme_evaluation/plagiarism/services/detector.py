import logging
import magic
from io import BytesIO
import PyPDF2
from pdfminer.high_level import extract_text
from django.core.exceptions import ValidationError
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from security.services.encryption import FileEncryptor
from cryptography.fernet import InvalidToken
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from scipy.sparse import vstack
import base64
import pickle

logger = logging.getLogger(__name__)

class PlagiarismDetectionError(Exception):
    """Exception personnalisée pour les erreurs de détection de plagiat"""
    pass

class PlagiarismDetector:
    def __init__(self):
        """Initialise le détecteur avec des paramètres optimisés"""
        self.vectorizer = TfidfVectorizer(
            stop_words=self._get_french_stopwords(),
            ngram_range=(1, 3),
            min_df=1,
            max_df=1.0,
            max_features=10000,
            analyzer='word'
        )
        self.nn_model = None
        self.submission_ids = []
        self._load_fingerprints()

    def _get_french_stopwords(self):
        """Retourne une liste complète de stopwords français"""
        return [
            'le', 'la', 'les', 'de', 'du', 'des', 'un', 'une', 'et', 'ou',
            'à', 'a', 'au', 'aux', 'en', 'dans', 'pour', 'par', 'sur', 'avec',
            'est', 'sont', 'son', 'ses', 'ces', 'cet', 'cette', 'mais', 'comme',
            'dans', 'pour', 'par', 'sur', 'sous', 'vers', 'avec', 'sans', 'entre',
            'chez', 'depuis', 'jusque', 'pendant', 'contre', 'dès', 'selon', 'durant'
        ]

    def _load_fingerprints(self):
        """Charge les empreintes avec gestion robuste des erreurs"""
        from plagiarism.models import DocumentFingerprint
        
        try:
            if not DocumentFingerprint.objects.exists():
                self._initialize_fingerprints()

            fingerprints = DocumentFingerprint.objects.exclude(tfidf_vector=None)
            texts = []
            submission_ids = []
            
            with ThreadPoolExecutor(max_workers=4) as executor:
                results = list(executor.map(self._process_fingerprint, fingerprints))
                
                for result in results:
                    if result:
                        sub_id, text = result
                        texts.append(text)
                        submission_ids.append(sub_id)

            if texts:
                # Ajustement dynamique des paramètres
                n_docs = len(texts)
                self.vectorizer.min_df = max(1, min(2, n_docs//3))
                self.vectorizer.max_df = min(0.95, 0.5 + 0.5/n_docs) if n_docs > 5 else 1.0

                # Traitement par lots
                batch_size = 100
                vectors = None
                
                for i in range(0, len(texts), batch_size):
                    batch = texts[i:i+batch_size]
                    batch_vectors = self.vectorizer.fit_transform(batch) if i == 0 else self.vectorizer.transform(batch)
                    
                    if vectors is None:
                        vectors = batch_vectors
                    else:
                        vectors = vstack([vectors, batch_vectors])

                self.nn_model = NearestNeighbors(
                    n_neighbors=min(5, len(texts)),
                    metric='cosine',
                    algorithm='brute'
                ).fit(vectors)
                self.submission_ids = submission_ids
                logger.info(f"{len(texts)} empreintes chargées (min_df={self.vectorizer.min_df}, max_df={self.vectorizer.max_df})")
            else:
                logger.warning("Aucune empreinte valide trouvée")
                self._initialize_fingerprints()

        except Exception as e:
            logger.error(f"Erreur chargement empreintes: {str(e)}", exc_info=True)
            raise PlagiarismDetectionError("Erreur initialisation base de données")

    def _process_fingerprint(self, fingerprint):
        """Traite une empreinte individuelle"""
        try:
            text = self._extract_text(fingerprint.submission)
            if text and len(text.split()) >= 10:  # Au moins 10 mots
                return (fingerprint.submission_id, text)
            return None
        except Exception as e:
            logger.warning(f"Erreur empreinte {fingerprint.id}: {str(e)}")
            return None

    def _extract_text(self, submission):
        """Méthode d'extraction robuste avec gestion des types bytes/str"""
        try:
            content = submission.get_file_content()
            if not content:
                raise ValidationError("Fichier vide")

            # Conversion en bytes si nécessaire
            if isinstance(content, str):
                content = content.encode('utf-8')

            # Tentative de déchiffrement
            try:
                encryptor = FileEncryptor()
                decrypted = encryptor.cipher.decrypt(content)
                if decrypted and len(decrypted) > 0:
                    if isinstance(decrypted, str):
                        decrypted = decrypted.encode('utf-8')
                    content = decrypted
            except InvalidToken:
                pass  # Fichier non chiffré
            except Exception as e:
                logger.warning(f"Erreur déchiffrement: {str(e)}")

            # Extraction selon le type de fichier
            if self._is_likely_pdf(content):
                text = self._extract_from_pdf(content)
                if text:
                    return text
                raise ValidationError("Échec extraction PDF")
            else:
                try:
                    text = content.decode('utf-8', errors='replace')
                    if text.strip():
                        return text
                    raise ValidationError("Fichier texte vide")
                except UnicodeDecodeError:
                    raise ValidationError("Format non supporté")

        except ValidationError as ve:
            raise ve
        except Exception as e:
            logger.error(f"Erreur extraction: {str(e)}", exc_info=True)
            raise ValidationError(f"Erreur traitement fichier: {str(e)}")

    def _is_likely_pdf(self, content):
        """Détection robuste des PDF"""
        if len(content) < 5:
            return False
            
        try:
            file_type = magic.from_buffer(content[:1024], mime=True)
            return file_type == 'application/pdf'
        except:
            return (content.startswith(b'%PDF') or b'%PDF' in content[:1024])

    def _extract_from_pdf(self, content):
        """Extraction PDF avec plusieurs méthodes"""
        # Méthode PyPDF2
        try:
            with BytesIO(content) as pdf_file:
                reader = PyPDF2.PdfReader(pdf_file)
                if reader.is_encrypted:
                    if not reader.decrypt(''):  # Essai avec mot vide
                        raise ValidationError("PDF protégé")
                
                text = "\n".join([p.extract_text() or '' for p in reader.pages])
                if text.strip():
                    return text
        except Exception as e:
            logger.warning(f"Échec PyPDF2: {str(e)}")

        # Méthode pdfminer
        try:
            text = extract_text(BytesIO(content))
            if text.strip():
                return text
        except Exception as e:
            logger.warning(f"Échec pdfminer: {str(e)}")

        return None

    def scan_submission(self, submission):
        """Analyse une soumission pour plagiat"""
        try:
            text = self._extract_text(submission)
            if not text or len(text.split()) < 20:
                raise ValidationError("Texte trop court ou vide")

            results = {
                'internal': [],
                'warnings': [],
                'overall_similarity': 0
            }

            if self.nn_model:
                vector = self.vectorizer.transform([text])
                distances, indices = self.nn_model.kneighbors(vector)
                
                matches = []
                for i in range(len(indices[0])):
                    similarity = round(float(1 - distances[0][i]) * 100, 2)
                    if similarity > 30:  # Seuil de similarité
                        sub_id = self.submission_ids[indices[0][i]]
                        if str(sub_id) != str(submission.id):
                            match = self._get_match_details(sub_id, similarity)
                            if match:
                                matches.append(match)
                
                if matches:
                    results['internal'] = sorted(matches, key=lambda x: x['similarity'], reverse=True)
                    results['overall_similarity'] = max(m['similarity'] for m in matches)
                else:
                    results['warnings'].append("Aucune similarité détectée")

            return results

        except ValidationError as e:
            raise
        except Exception as e:
            logger.error(f"Erreur analyse: {str(e)}", exc_info=True)
            raise PlagiarismDetectionError(f"Erreur analyse: {str(e)}")

    def _get_match_details(self, submission_id, similarity):
        """Récupère les détails d'une correspondance"""
        from submissions.models import Submission
        
        try:
            target = Submission.objects.get(pk=submission_id)
            return {
                'submission_id': str(submission_id),
                'similarity': similarity,
                'student': target.student.get_full_name(),
                'exercise': target.exercise.title,
                'date': target.submission_date.strftime("%Y-%m-%d"),
                'excerpt': self._get_match_excerpt(target)
            }
        except Exception as e:
            logger.error(f"Erreur détails correspondance: {str(e)}")
            return None

    def _get_match_excerpt(self, target_submission):
        """Génère un extrait du document similaire"""
        try:
            content = target_submission.get_file_content()
            if content:
                if isinstance(content, str):
                    text = content
                else:
                    text = content.decode('utf-8', errors='ignore')
                return text[:200] + ('...' if len(text) > 200 else '')
            return "Extrait non disponible"
        except Exception as e:
            logger.warning(f"Erreur génération extrait: {str(e)}")
            return "Erreur génération extrait"

    def _initialize_fingerprints(self):
        """Initialise les empreintes si base vide"""
        from plagiarism.models import DocumentFingerprint
        from submissions.models import Submission
        
        try:
            count = 0
            for submission in Submission.objects.all():
                try:
                    text = self._extract_text(submission)
                    if text:
                        vector = self.vectorizer.fit_transform([text])
                        DocumentFingerprint.objects.create(
                            submission=submission,
                            tfidf_vector=self._serialize_vector(vector)
                        )
                        count += 1
                except Exception as e:
                    logger.warning(f"Erreur empreinte {submission.id}: {str(e)}")

            logger.info(f"{count} nouvelles empreintes créées")
        except Exception as e:
            logger.error(f"Erreur initialisation empreintes: {str(e)}", exc_info=True)
            raise

    def _serialize_vector(self, vector):
        """Sérialise un vecteur TF-IDF pour stockage en bytes"""
        try:
            serialized = pickle.dumps(vector)
            if not isinstance(serialized, bytes):
                raise ValueError("La sérialisation doit produire des bytes")
            return serialized
        except Exception as e:
            logger.error(f"Erreur sérialisation: {str(e)}")
            raise

    def update_fingerprint(self, submission):
        """Met à jour une empreinte individuelle"""
        from plagiarism.models import DocumentFingerprint
        
        try:
            text = self._extract_text(submission)
            if not text or len(text.split()) < 10:
                return False
                
            vector = self.vectorizer.transform([text])
            if vector is None or vector.shape[1] == 0:
                return False
                
            DocumentFingerprint.objects.update_or_create(
                submission=submission,
                defaults={'tfidf_vector': self._serialize_vector(vector)}
            )
            return True
        except Exception as e:
            logger.error(f"Erreur mise à jour empreinte: {str(e)}")
            return False