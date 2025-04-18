from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls')),
    path('api/exercises/', include('exercises.urls')),
    path('api/submissions/', include('submissions.urls')),
    path('api/evaluation/', include('evaluation.urls')),
    path('accounts/', include('allauth.urls')),
    path('exercises/', include('exercises.urls_template')),  # Templates
    path('', include('pages.urls')),  # Pour la page d'accueil
    path('performance/', include('accounts.urls')),
    path('notifications/', include('notifications.urls', namespace='notifications')),
    path('security/', include('security.urls')),
]
# Servir les fichiers media en développements
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)