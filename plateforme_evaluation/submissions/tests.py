from submissions.services import extract_text_from_file
import tempfile
import os

# Test avec fichier texte réel
with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp:
    tmp.write(b"Contenu de test")
    tmp_path = tmp.name

try:
    print(f"Test d'extraction sur {tmp_path}:")
    print(extract_text_from_file(tmp_path))
finally:
    os.unlink(tmp_path)  # Nettoyage

    # tests.py
from django.test import TestCase
from submissions.services import extract_text_from_file
from io import BytesIO
from reportlab.pdfgen import canvas

class PDFExtractionTest(TestCase):
    def test_pdf_extraction(self):
        # Génère un PDF de test
        buffer = BytesIO()
        p = canvas.Canvas(buffer)
        p.drawString(100, 100, "TEST UNITAIRE PDF")
        p.save()
        
        # Test extraction
        with tempfile.NamedTemporaryFile(suffix='.pdf') as tmp:
            tmp.write(buffer.getvalue())
            tmp.seek(0)
            result = extract_text_from_file(tmp.name)
            self.assertIn("TEST UNITAIRE", result)