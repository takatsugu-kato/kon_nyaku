from django import forms
from translate.models import File

class DocumentForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ('name', 'document')
