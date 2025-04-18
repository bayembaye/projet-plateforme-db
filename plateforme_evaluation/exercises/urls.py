from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet,
    ExerciseViewSet,
    ExerciseFileViewSet,
    SolutionViewSet,
    ExerciseGroupViewSet
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'exercises', ExerciseViewSet)
router.register(r'exercise-files', ExerciseFileViewSet)
router.register(r'solutions', SolutionViewSet)
router.register(r'exercise-groups', ExerciseGroupViewSet)

urlpatterns = [
    path('', include(router.urls)),
]