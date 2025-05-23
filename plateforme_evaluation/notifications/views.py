# notifications/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.urls import reverse
from .models import Notification
import json

@login_required
def list_notifications(request):
    """Affiche la liste des notifications de l'utilisateur"""
    notifications = request.user.notifications.all()
    
    # Si demande JSON (pour l'API)
    if request.GET.get('json'):
        notifications_data = []
        for notification in notifications[:10]:  # Limiter à 10 pour les performances
            try:
                target_url = notification.get_absolute_url()
            except:
                target_url = None
            
            notifications_data.append({
                'id': notification.id,
                'verb': notification.verb,
                'description': notification.description,
                'unread': notification.unread,
                'created_at': notification.created_at.isoformat(),
                'target_url': target_url
            })
        
        return JsonResponse({
            'count': notifications.count(),
            'notifications': notifications_data
        })
    
    # Sinon afficher la page complète
    return render(request, 'notifications/full_list.html', {
        'notifications': notifications
    })# notifications/views.py

@login_required
def list_notifications(request):
    notifications = request.user.notifications.all()
    
    if request.GET.get('json'):
        notifications_data = []
        for notification in notifications[:10]:
            try:
                target_url = notification.get_absolute_url()
            except:
                target_url = None
                
            notifications_data.append({
                'id': notification.id,
                'verb': notification.verb,
                'description': notification.description,
                'unread': notification.unread,
                'created_at': notification.created_at.isoformat(),
                'target_url': target_url
            })
        
        return JsonResponse({
            'count': notifications.count(),
            'notifications': notifications_data
        })
    
    return render(request, 'notifications/full_list.html', {
        'notifications': notifications
    })
@login_required
def test_notification(request):
    """Crée une notification de test pour l'utilisateur actuel"""
    notification = Notification.objects.create_user_notification(
        user=request.user,
        verb="Notification de test",
        description="Ceci est une notification de test créée manuellement."
    )
    return redirect('notifications:list')# notifications/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.urls import reverse
from .models import Notification
import json

@login_required
def list_notifications(request):
    """Affiche la liste des notifications de l'utilisateur"""
    notifications = request.user.notifications.all()
    
    # Si demande JSON (pour l'API)
    if request.GET.get('json'):
        notifications_data = []
        for notification in notifications[:10]:  # Limiter à 10 pour les performances
            target_url = notification.get_absolute_url()
            
            notifications_data.append({
                'id': notification.id,
                'verb': notification.verb,
                'description': notification.description,
                'unread': notification.unread,
                'created_at': notification.created_at.isoformat(),
                'target_url': target_url
            })
        
        return JsonResponse({
            'count': notifications.count(),
            'notifications': notifications_data
        })
    
    # Sinon afficher la page complète
    return render(request, 'notifications/full_list.html', {
        'notifications': notifications
    })

@login_required
def get_unread_count(request):
    """Renvoie le nombre de notifications non lues"""
    count = request.user.notifications.unread().count()
    return JsonResponse({'count': count})

@login_required
@require_POST
def mark_all_as_read(request):
    """Marque toutes les notifications comme lues"""
    request.user.notifications.filter(read=False).update(read=True)
    return JsonResponse({'status': 'success'})

@login_required
def test_notification(request):
    """Crée une notification de test pour l'utilisateur actuel"""
    notification = Notification.objects.create_user_notification(
        user=request.user,
        verb="Notification de test",
        description="Ceci est une notification de test créée manuellement."
    )
    return redirect('notifications:list')