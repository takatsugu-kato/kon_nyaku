import os

from django import forms
from translate.models import File

from .consts import LANG
from .consts import SUPPORTED_FILE_FORMAT

class DocumentForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ('name', 'source_lang', 'target_lang', 'document', 'file_session_key', 'delete_format_tag')

        SOURCE_LANG = LANG
        TARGET_LANG = LANG

        widgets = {
            'name': forms.HiddenInput(attrs={'id': "id_name"}),
            'delete_format_tag': forms.CheckboxInput(),
            'file_session_key': forms.HiddenInput(),
            'document': forms.FileInput(attrs={'style': 'display:none', 'accept': '.xlsx,.docx,.pptx'}),
            'source_lang': forms.Select(choices=SOURCE_LANG),
            'target_lang': forms.Select(choices=TARGET_LANG),
        }

    def clean_name(self):
        name = self.cleaned_data['name']
        path_split = os.path.splitext(name)
        if path_split[1] not in SUPPORTED_FILE_FORMAT:
            raise forms.ValidationError('This file does not support.')
        return name

    # def clean_source_lang(self): #ToDo source_langとtarget_langが同じだったときのバリデーションをいれる
    #     source_lang = self.cleaned_data['source_lang']
    #     raise forms.ValidationError('source_lang のバリデーションに引っかかりました。')


