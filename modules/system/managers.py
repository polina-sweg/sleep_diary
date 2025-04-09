# system/models.py
from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    """Кастомный менеджер для модели User с email в качестве идентификатора"""
    use_in_migrations = True

    def _create_user(self, email, username, password, **extra_fields):
        if not email:
            raise ValueError('Отсутствует адрес электронной почты.')
        if not username:
            raise ValueError('Отсутствует имя пользователя.')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, username, password, **extra_fields)

    def create_superuser(self, email, username, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(email, username, password, **extra_fields)
