from django.urls import path
from django.contrib.auth.decorators import login_required
from .views import (
    ExerciseListView,
    ExerciseCreateView,
    ExerciseDetailView,
    ExerciseUpdateView,
    ExerciseDeleteView,
    ExerciseFileCreateView,
    ExerciseFileDeleteView,
    SolutionCreateView,
    ExerciseGroupCreateView,
    CategoryCreateView,
    SolutionDeleteView,
    SetDefaultSolutionView
)
from .views import ProfessorStatisticsView  # Import correct

urlpatterns = [
    # Liste/Création
    path('', login_required(ExerciseListView.as_view()), name='exercise-list'),
    path('new/', login_required(ExerciseCreateView.as_view()), name='exercise-create'),
    
    # Détail/Modification
    path('<int:pk>/', ExerciseDetailView.as_view(), name='exercise-detail'),
    path('<int:pk>/edit/', login_required(ExerciseUpdateView.as_view()), name='exercise-update'),
    path('<int:pk>/delete/', ExerciseDeleteView.as_view(), name='exercise-delete'),
    
    # Fichiers/Solutions
    path('<int:exercise_id>/add-file/', login_required(ExerciseFileCreateView.as_view()), name='exercisefile-create'),
    path('files/<int:pk>/delete/', ExerciseFileDeleteView.as_view(), name='exercisefile-delete'),
    path('<int:exercise_id>/add-solution/', login_required(SolutionCreateView.as_view()), name='solution-create'),
    
    # Catégories
    path('categories/new/', login_required(CategoryCreateView.as_view()), name='category-create'),
    
    # Groupes
    path('groups/new/', login_required(ExerciseGroupCreateView.as_view()), name='group-create'),
    path('professor-stats/', ProfessorStatisticsView.as_view(), name='professor_stats'),
    path('<int:exercise_id>/add-solution/', login_required(SolutionCreateView.as_view()), name='solution-create'),
    path('solutions/<int:pk>/set-default/', login_required(SetDefaultSolutionView.as_view()), name='solution-set-default'),
    path('solutions/<int:pk>/delete/', login_required(SolutionDeleteView.as_view()), name='solution-delete'),
    path('<int:pk>/', ExerciseDetailView.as_view(), name='exercise-detail'),
    path('<int:exercise_id>/add-solution/', SolutionCreateView.as_view(), name='solution-create'),
]

