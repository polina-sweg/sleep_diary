# Generated by Django 5.0.11 on 2025-04-07 12:51

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0002_remove_user_language_alter_user_date_of_birth_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(help_text='Обязательно. 4-12 символов. Только буквы, цифры и подчеркивания.', max_length=12, validators=[django.core.validators.RegexValidator(message='Имя пользователя может содержать только буквы, цифры и подчеркивания.', regex='^[a-zA-Z0-9_]+$')], verbose_name='имя пользователя'),
        ),
    ]
