# Generated by Django 2.1.7 on 2019-03-15 05:30

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('translate', '0002_auto_20190315_1340'),
    ]

    operations = [
        migrations.AddField(
            model_name='file',
            name='document',
            field=models.FileField(default=django.utils.timezone.now, upload_to='documents/'),
            preserve_default=False,
        ),
    ]
