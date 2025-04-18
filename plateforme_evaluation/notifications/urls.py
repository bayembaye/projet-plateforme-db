# notifications/urls.py
from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('list/', views.list_notifications, name='list'),
    path('unread-count/', views.get_unread_count, name='unread_count'),
    path('mark-all-read/', views.mark_all_as_read, name='mark_all_read'),
    path('test/', views.test_notification, name='test'),
]