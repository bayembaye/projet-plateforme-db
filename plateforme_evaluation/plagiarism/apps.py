from django.apps import AppConfig

class PlagiarismConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'plagiarism'
    
    def ready(self):
        import plagiarism.signals  # Pour les signaux