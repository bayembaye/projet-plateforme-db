from django import forms
from .models import ExerciseFile, Solution


class ExerciseFileForm(forms.ModelForm):
    class Meta:
        model = ExerciseFile
        fields = ['file', 'file_name', 'file_type', 'is_statement']
        widgets = {
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.txt,.zip,.sql,.py'  # Types de fichiers acceptés
            }),
            'file_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom descriptif du fichier'
            }),
            'file_type': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: PDF, SQL, Python, etc.'
            }),
            'is_statement': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'file': 'Fichier',
            'file_name': 'Nom du fichier',
            'file_type': 'Type de fichier',
            'is_statement': 'Est-ce l\'énoncé principal ?'
        }
        help_texts = {
            'is_statement': 'Cocher si ce fichier contient l\'énoncé principal de l\'exercice'
        }

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Validation de la taille (20MB max)
            max_size = 20 * 1024 * 1024
            if file.size > max_size:
                raise forms.ValidationError(f"Le fichier est trop volumineux. Taille maximale: {max_size/1024/1024}MB.")
            
            # Validation de l'extension
            valid_extensions = ['.pdf', '.doc', '.docx', '.txt', '.zip', '.sql', '.py']
            if not any(file.name.lower().endswith(ext) for ext in valid_extensions):
                raise forms.ValidationError("Type de fichier non supporté. Formats acceptés: PDF, DOC, TXT, ZIP, SQL, PY.")
        
        return file

class SolutionForm(forms.ModelForm):
    class Meta:
        model = Solution
        fields = ['description', 'file']
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 5}),
            'file': forms.FileInput(attrs={'class': 'form-input'}),
        }