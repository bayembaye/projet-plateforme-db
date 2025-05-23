from django.apps import AppConfig

class SubmissionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'submissions'

    def ready(self):
        # Import des signaux après que les apps soient chargées
        from django.db.models.signals import post_save
        from . import signals  # noqa
        post_save.connect(signals.submission_notification, sender='submissions.Submission')