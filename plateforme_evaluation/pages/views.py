# pages/views.py
from django.views.generic import TemplateView
from exercises.models import Exercise

class HomeView(TemplateView):
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recent_exercises'] = Exercise.objects.filter(is_active=True).order_by('-created_at')[:3]
        return context