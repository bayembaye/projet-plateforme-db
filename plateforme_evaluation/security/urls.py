from django.urls import path
from .views.web import SecurityLogView, KeyManagementView
from security.views.web import SecurityLogView, KeyManagementView

app_name = 'security'

urlpatterns = [
    path('logs/', SecurityLogView.as_view(), name='logs'),
    path('keys/', KeyManagementView.as_view(), name='keys'),
]