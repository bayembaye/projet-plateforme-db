from django.shortcuts import redirect
from django.urls import reverse

class PlagiarismAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Vérifie si c'est une redirection vers le login pour une URL de plagiat
        if response.status_code == 302 and 'login' in response.url:
            if request.path.startswith('/plagiarism/'):
                login_url = reverse('account_login')
                return redirect(f'{login_url}?next={request.path}')
        
        return response