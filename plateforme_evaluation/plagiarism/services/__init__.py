# services/__init__.py
from .detector import PlagiarismDetector
from .text_processing import preprocess_text

__all__ = ['PlagiarismDetector', 'preprocess_text']