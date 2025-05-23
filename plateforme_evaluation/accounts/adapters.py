from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.exceptions import ImmediateHttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        user = sociallogin.user
        if user.id:  # Si l'utilisateur existe déjà
            return
        
        # Vérifier si l'email existe déjà
        if user.email and self._email_exists(user.email):
            messages.warning(request, "Un compte existe déjà avec cette adresse email. Connectez-vous d'abord avec votre compte local, puis associez ce compte social.")
            raise ImmediateHttpResponse(redirect(reverse('account_login')))
    
    def _email_exists(self, email):
        from allauth.account.models import EmailAddress
        return EmailAddress.objects.filter(email=email, verified=True).exists()