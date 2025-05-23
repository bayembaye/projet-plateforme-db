from django.urls import path
from .views import (
    SubmissionCreateView,
    SubmissionDetailView,
    SubmissionListView,
    SubmissionUpdateView,
    GradeSubmissionView, 
    SubmissionDeleteView,
    DisputeSubmissionView,
AutoCorrectSubmissionView
)
from django.urls import path
from .views import SubmissionUpdateView

urlpatterns = [
    path('<uuid:pk>/delete/', SubmissionDeleteView.as_view(), name='submission-delete'),
    path('<uuid:pk>/', SubmissionDetailView.as_view(), name='submission-detail'),
    path('<uuid:pk>/edit/', SubmissionUpdateView.as_view(), name='submission-update'),
    path('<uuid:pk>/grade/', GradeSubmissionView.as_view(), name='grade-submission'),
    path('<uuid:pk>/dispute/', DisputeSubmissionView.as_view(), name='dispute-submission'),
    path('', SubmissionListView.as_view(), name='submission-list'),
    path('exercise/<int:exercise_id>/submit/', SubmissionCreateView.as_view(), name='submission-create'),
    path('<uuid:pk>/auto-correct/', AutoCorrectSubmissionView.as_view(), name='auto-correct-submission'),
]