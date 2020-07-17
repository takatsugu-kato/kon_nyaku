"""
models
"""
from django.db import models

class Glossary(models.Model):
    """Glossary"""
    name = models.CharField('File name', max_length=255)
    status = models.IntegerField('Status', blank=True, default=0)
    terms = models.IntegerField('Terms', blank=True, default=0)
    source_lang = models.CharField('Source Language', max_length=8, default='')
    target_lang = models.CharField('Target Language', max_length=8, default='')
    created_date = models.DateTimeField('Created', auto_now_add=True)
    modified_date = models.DateTimeField('Modified', auto_now=True)
    document = models.FileField('File', upload_to='media/glossary')

    def __str__(self):
        return self.name

class File(models.Model):
    """File"""
    name = models.CharField('File name', max_length=255)
    file_session_key = models.CharField('Session Key', max_length=40, default='')
    ip_address = models.GenericIPAddressField('IP Address', default="")
    status = models.IntegerField('Status', blank=True, default=0)
    delete_format_tag = models.BooleanField("Delete Format Tags", default=False)
    source_lang = models.CharField('Source Language', max_length=8, default='')
    target_lang = models.CharField('Target Language', max_length=8, default='')
    change_to_jotai = models.BooleanField('Change to Jotai', default=False)
    glossary_to_use = models.ForeignKey(Glossary, models.SET_NULL, blank=True, null=True,)
    progress = models.IntegerField('Progress', blank=True, default=0)
    created_date = models.DateTimeField('Created', auto_now_add=True)
    modified_date = models.DateTimeField('Modified', auto_now=True)
    document = models.FileField('File', upload_to='media/')
    chara_count = models.PositiveIntegerField('Character Count', blank=True, default=0)
    delete_flag = models.BooleanField('Deleted', blank=True, default=0)

    def __str__(self):
        return self.name

class Text(models.Model):
    """Text"""
    file_session_key = models.CharField('Session Key', max_length=40, default='')
    ip_address = models.GenericIPAddressField('IP Address')
    status = models.CharField('Status', max_length=16, default='')
    source_lang = models.CharField('Source Language', max_length=8, default='')
    target_lang = models.CharField('Target Language', max_length=8, default='')
    created_date = models.DateTimeField('Created', auto_now_add=True)
    modified_date = models.DateTimeField('Modified', auto_now=True)
    chara_count = models.PositiveIntegerField('Character Count', blank=True, default=0)

    def __str__(self):
        return self.ip_address
