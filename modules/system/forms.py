from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

User = get_user_model()


class SignUpForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput,
        validators=[
            RegexValidator(
                regex=r'^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()]).{8,}$',
                message='Пароль должен содержать минимум 8 символов, одну заглавную букву, цифру и специальный символ'
            )
        ]
    )
    password2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'desired_sleep_hours']
        labels = {
            'desired_sleep_hours': 'Норма часов сна в сутки'
        }
        help_texts = {
            'username': 'От 4 до 12 символов. Только буквы, цифры и подчёркивания.'
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Этот email уже зарегистрирован')
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError('Пароли не совпадают')
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'autofocus': True})
    )


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'desired_sleep_hours', 'date_of_birth',
                  'gender', 'profile_picture', 'phone_number']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'desired_sleep_hours': forms.NumberInput(attrs={'placeholder': 'Норма часов сна в сутки'}),
            'phone_number': forms.TextInput(attrs={'placeholder': 'Номер телефона'}),
        }

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['readonly'] = True
