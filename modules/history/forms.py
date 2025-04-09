from django import forms
from datetime import timedelta
from .models import Record

from django import forms
from .models import Record


class RecordCreateForm(forms.ModelForm):
    class Meta:
        model = Record
        fields = ['sleep_start', 'sleep_end', 'wake_quality', 'alertness', 'note']
        widgets = {
            'sleep_start': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'sleep_end': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        sleep_start = cleaned_data.get('sleep_start')
        sleep_end = cleaned_data.get('sleep_end')

        if sleep_start and sleep_end:
            if sleep_start >= sleep_end:
                raise forms.ValidationError("Время начала сна должно быть раньше времени окончания.")

            if sleep_end - sleep_start > timedelta(hours=24):
                raise forms.ValidationError(
                    "Продолжительность сна не может превышать 24 часов. "
                    "Пожалуйста, проверьте введенные данные."
                )

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.user = self.user
        if commit:
            instance.save()
        return instance


class RecordEditForm(forms.ModelForm):
    class Meta:
        model = Record
        fields = ['sleep_start', 'sleep_end', 'wake_quality', 'alertness', 'note']
        widgets = {
            'sleep_start': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'sleep_end': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            self.fields['sleep_start'].initial = self.instance.sleep_start.strftime('%Y-%m-%dT%H:%M')
            self.fields['sleep_end'].initial = self.instance.sleep_end.strftime('%Y-%m-%dT%H:%M')

    def clean(self):
        cleaned_data = super().clean()
        sleep_start = cleaned_data.get('sleep_start')
        sleep_end = cleaned_data.get('sleep_end')

        if sleep_start and sleep_end:
            if sleep_start >= sleep_end:
                raise forms.ValidationError("Время начала сна должно быть раньше времени окончания.")

            sleep_duration = sleep_end - sleep_start
            if sleep_duration.total_seconds() > 24 * 3600:
                raise forms.ValidationError("Продолжительность сна не может превышать 24 часа.")
