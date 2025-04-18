# evaluation/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Importation des vues (à implémenter plus tard)
# from .views import EvaluationViewSet, etc.

router = DefaultRouter()
# router.register(r'evaluations', EvaluationViewSet)
# etc.

urlpatterns = [
    path('', include(router.urls)),
]