# accounts/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import StudentProfileUpdateView
from django.urls import path
from .views import update_theme_preference
from .views import StudentPerformanceView


from .views import (
    UserViewSet, 
    StudentProfileUpdateView, 
    ProfessorProfileUpdateView,
    profile_view
)

router = DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('student-profile/update/', StudentProfileUpdateView.as_view(), name='student-profile-update'),
    path('professor-profile/update/', ProfessorProfileUpdateView.as_view(), name='professor-profile-update'),
    path('profile/', profile_view, name='account_profile'),  # Nouvelle route pour le profil
    path('api/update-theme/', update_theme_preference, name='update_theme_preference'),
    path('student-profile/update/', StudentProfileUpdateView.as_view(), name='student-profile-update'),
    path('professor-profile/update/', ProfessorProfileUpdateView.as_view(), name='professor-profile-update'),
    path('student-profile/update/', 
         StudentProfileUpdateView.as_view(), 
         name='student-profile-update'),
    
    path('professor-profile/update/', 
         ProfessorProfileUpdateView.as_view(), 
         name='professor-profile-update'),
    path('accounts/', include('allauth.urls')),
    path('student/performance/', StudentPerformanceView.as_view(), name='student_performance'),
]

