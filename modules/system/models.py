from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, MinLengthValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from modules.system.managers import UserManager


class User(AbstractUser):
    """Кастомная модель пользователя с email в качестве идентификатора"""

    username_validator = RegexValidator(
        regex=r'^[a-zA-Z0-9_]+$',
        message=_('Имя пользователя может содержать только буквы, цифры и подчеркивания.')
    )

    username = models.CharField(
        _('имя пользователя'),
        max_length=12,
        validators=[username_validator],
        help_text=_('Обязательно. 4-12 символов. Только буквы, цифры и подчеркивания.'),
    )
    email = models.EmailField(
        _('адрес электронной почты'),
        unique=True,
        error_messages={
            'unique': _('Пользователь с таким email уже существует.'),
        }
    )
    desired_sleep_hours = models.PositiveSmallIntegerField(
        _('норма часов сна'),
        default=8,
        help_text=_('Норма часов сна в сутки')
    )

    date_of_birth = models.DateField(
        _('дата рождения'),
        null=True,
        blank=True,
        help_text=_('Дата рождения')
    )

    gender = models.CharField(
        _('пол'),
        max_length=10,
        choices=[('M', _('Мужской')), ('F', _('Женский'))],
        null=True,
        blank=True,
        help_text=_('Пол')
    )

    profile_picture = models.ImageField(
        _('фотография профиля'),
        upload_to='avatars/',
        null=True,
        blank=True,
        help_text=_('Загрузите фотографию профиля')
    )

    phone_number = models.CharField(
        _('номер телефона'),
        max_length=15,
        blank=True,
        null=True,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$')],
        help_text=_('Номер телефона')
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    def __str__(self):
        return self.email

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    @property
    def sleep_norm_seconds(self) -> int:
        return self.desired_sleep_hours * 3600
