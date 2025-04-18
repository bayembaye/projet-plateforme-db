from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, CreateView
from ..models import SecurityEvent, EncryptionKey

class SecurityLogView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = SecurityEvent
    template_name = 'security/logs.html'
    permission_required = 'security.view_securityevent'
    paginate_by = 50
    
    def get_queryset(self):
        return super().get_queryset().select_related('user')

class KeyManagementView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = EncryptionKey
    template_name = 'security/keys.html'
    permission_required = 'security.view_encryptionkey'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_keys'] = EncryptionKey.objects.filter(active=True)
        return context