# Generated by Django 2.2.2 on 2020-06-19 07:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('translate', '0012_glossary_terms'),
    ]

    operations = [
        migrations.AddField(
            model_name='glossary',
            name='glossary_id',
            field=models.CharField(default='', max_length=255, verbose_name='Glossary ID'),
        ),
    ]
