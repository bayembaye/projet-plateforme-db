from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Submission

class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['file', 'comment']
        widgets = {
            'file': forms.FileInput(attrs={'required': True}),
            'comment': forms.Textarea(attrs={'rows': 3})
        }

    def __init__(self, *args, **kwargs):
        self.exercise = kwargs.pop('exercise', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        
        # Utilisez self.exercise au lieu de self.instance.exercise
        if self.exercise and self.exercise.deadline and self.exercise.deadline < timezone.now():
            raise ValidationError("La date limite pour cet exercice est dépassée")
        
        file = cleaned_data.get('file')
        if file:
            max_size = 10 * 1024 * 1024  # 10MB
            if file.size > max_size:
                raise ValidationError(f"Le fichier est trop volumineux. Taille maximale: {max_size/1024/1024}MB")
            
            valid_extensions = ['.sql', '.pdf', '.zip', '.txt']
            if not any(file.name.lower().endswith(ext) for ext in valid_extensions):
                raise ValidationError("Type de fichier non supporté. Formats acceptés: SQL, PDF, ZIP, TXT")
        
        return cleaned_data