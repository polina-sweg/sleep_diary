# Generated by Django 5.1.5 on 2025-03-28 15:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='record',
            name='sleep_duration',
            field=models.DurationField(blank=True, editable=False, help_text='Продолжительность сна, вычисляется автоматически.', null=True, verbose_name='Продолжительность сна'),
        ),
    ]
