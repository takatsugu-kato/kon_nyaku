# Generated by Django 2.1.7 on 2019-03-15 04:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('translate', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='file',
            old_name='filename',
            new_name='name',
        ),
    ]