from django.urls import path
from django.contrib.auth.decorators import login_required  # Ajoutez cette importation
from . import views

app_name = 'plagiarism'

urlpatterns = [
    path('scans/', views.PlagiarismScanListView.as_view(), name='scan-list'),
    path('scans/<uuid:pk>/', login_required(views.PlagiarismScanDetailView.as_view()), name='scan-detail'),
    path('scan/<uuid:submission_id>/', views.start_plagiarism_scan, name='start-scan'),
    path('api/scan/<uuid:submission_id>/', views.start_plagiarism_scan_api, name='start-scan-api'),
]