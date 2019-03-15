from django.db import models
from django.utils import timezone

class File(models.Model):
    """ファイル"""
    name = models.CharField('ファイル名', max_length=255)
    status = models.IntegerField('ステータス', blank=True, default=0)
    progress = models.IntegerField('進捗', blank=True, default=0)
    created_date = models.DateTimeField('作成日', auto_now_add=True)
    modified_date = models.DateTimeField('変更日', auto_now=True)
    document = models.FileField('ファイル', upload_to='media/')

    def __str__(self):
        return self.name
