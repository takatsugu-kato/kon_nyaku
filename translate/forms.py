from django import forms
from translate.models import File

from .consts import LANG

class DocumentForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ('name', 'source_lang', 'target_lang', 'document', 'file_session_key')

        SOURCE_LANG = LANG
        TARGET_LANG = LANG

        widgets = {
            'name': forms.HiddenInput(attrs={'id': "id_name"}),
            'document': forms.FileInput(attrs={'class': 'form-control'}),
            'source_lang': forms.Select(choices=SOURCE_LANG, attrs={'class': 'form-control'}),
            'target_lang': forms.Select(choices=TARGET_LANG, attrs={'class': 'form-control'}),
        }

