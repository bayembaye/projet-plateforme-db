# accounts/forms.py
from allauth.account.forms import SignupForm
from django import forms
from .models import User
from django import forms
from .models import StudentProfile, ProfessorProfile, User

class CustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=30, label='First Name')
    last_name = forms.CharField(max_length=30, label='Last Name')
    role = forms.ChoiceField(choices=User.Role.choices, label='Role')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'username' in self.fields:
            del self.fields['username']
    
    def save(self, request):
        user = super().save(request)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.role = self.cleaned_data['role']
        user.save()
        return user
    

from django import forms
from .models import StudentProfile, ProfessorProfile, User

class StudentProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    
    class Meta:
        model = StudentProfile
        fields = ['first_name', 'last_name', 'student_id', 'academic_level']

class ProfessorProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    
    class Meta:
        model = ProfessorProfile
        fields = ['first_name', 'last_name', 'faculty_id', 'department', 'specialization']    