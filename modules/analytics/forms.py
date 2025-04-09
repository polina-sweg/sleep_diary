from django import forms
from django.utils import timezone


class DateRangeForm(forms.Form):
    start_date = forms.DateField(
        label='Начало периода',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'filter-input',
            'max': timezone.now().date().isoformat()
        }),
        required=False
    )

    end_date = forms.DateField(
        label='Конец периода',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'filter-input',
            'max': timezone.now().date().isoformat()
        }),
        required=False
    )

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("Дата начала выбранного периода не может быть позже даты окончания")

        return cleaned_data