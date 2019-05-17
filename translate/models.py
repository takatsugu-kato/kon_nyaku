from django.db import models
from django.utils import timezone

class File(models.Model):
    """File"""
    name = models.CharField('File name', max_length=255)
    file_session_key = models.CharField('Session Key', max_length=40, default='')
    status = models.IntegerField('Status', blank=True, default=0)
    source_lang = models.CharField('Source Language', max_length=8, default='')
    target_lang = models.CharField('Target Language', max_length=8, default='')
    progress = models.IntegerField('Progress', blank=True, default=0)
    created_date = models.DateTimeField('Created', auto_now_add=True)
    modified_date = models.DateTimeField('Modified', auto_now=True)
    document = models.FileField('File', upload_to='media/')

    def __str__(self):
        return self.name
