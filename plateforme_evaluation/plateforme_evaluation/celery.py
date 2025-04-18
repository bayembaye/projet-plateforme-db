from __future__ import absolute_import
import os
from celery import Celery
from django.conf import settings

# Définir le module Django par défaut
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'votre_projet.settings')

app = Celery('votre_projet')

# Configuration avec les paramètres Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Découverte automatique des tâches
app.autodiscover_tasks()

# Configuration des tâches périodiques
app.conf.beat_schedule = {
    'record-student-performance': {
        'task': 'accounts.tasks.record_student_performance',
        'schedule': 604800.0,  # 7 jours en secondes
    },
}