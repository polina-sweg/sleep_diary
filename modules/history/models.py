from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
import requests
import os

User = get_user_model()


def get_sleep_recommendation(prompt):
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        return "API-ключ не найден."

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}]
    }

    response = requests.post(
        "https://api.deepseek.com/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=10
    )
    # Чекаем ошибки
    # print("Status Code:", response.status_code)
    # print("Response Headers:", response.headers)
    # print("Response Text:", response.text)
    # print()

    # response.raise_for_status()
    try:
        return response.json()["choices"][0]["message"]["content"]
    except Exception:
        return "Не удалось получить рекомендацию."

class Record(models.Model):
    """
    Модель записи о сне
    """
    WAKE_QUALITY_CHOICES = [
        (1, 'Трудно проснулся'),
        (2, 'Нормальные ощущения'),
        (3, 'Легко проснулся'),
    ]

    ALERTNESS_CHOICES = [
        (1, 'Очень уставший'),
        (2, 'Средний уровень бодрости'),
        (3, 'Полный энергии'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sleep_records',
        verbose_name='Пользователь',
        help_text='Пользователь, к которому относится запись о сне.'
    )
    sleep_start = models.DateTimeField(
        verbose_name='Время отхода ко сну',
        help_text='Дата и время, когда пользователь лег спать.'
    )
    sleep_end = models.DateTimeField(
        verbose_name='Время пробуждения',
        help_text='Дата и время, когда пользователь проснулся.'
    )
    sleep_duration = models.DurationField(
        verbose_name='Продолжительность сна',
        blank=True,
        null=True,
        editable=False,
        help_text='Продолжительность сна, вычисляется автоматически.'
    )
    wake_quality = models.PositiveSmallIntegerField(
        choices=WAKE_QUALITY_CHOICES,
        verbose_name='Лёгкость пробуждения',
        default=2,
        help_text='Оценка лёгкости пробуждения.'
    )
    alertness = models.PositiveSmallIntegerField(
        choices=ALERTNESS_CHOICES,
        verbose_name='Уровень бодрости в течение дня',
        default=2,
        help_text='Оценка уровня бодрости пользователя в течение дня.'
    )
    note = models.TextField(
        verbose_name='Заметка о сне',
        blank=True,
        help_text='Дополнительные заметки пользователя о сне.'
    )
    recommendation = models.TextField(
        verbose_name="Рекомендация по улучшению сна",
        blank=True,
        null=True,
        help_text="Автоматически сгенерированная рекомендация по улучшению сна."
    )

    class Meta:
        db_table = 'app_sleep_records'
        ordering = ['-sleep_start']
        verbose_name = 'Запись о сне'

    def __str__(self):
        return f"Запись о сне от {self.sleep_end.date()}"

    def get_absolute_url(self):
        return reverse('records_detail', kwargs={'pk': self.pk})

    def formatted_sleep_duration(self):
        if self.sleep_duration:
            total_seconds = int(self.sleep_duration.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            return f"{hours} ч {minutes} мин"
        return "Не указано"

    def clean(self):
        if self.sleep_start and self.sleep_end:
            if self.sleep_start >= self.sleep_end:
                raise ValidationError("Время пробуждения должно быть позже времени засыпания.")

    def save(self, *args, **kwargs):
        if self.sleep_start and self.sleep_end:
            self.sleep_duration = self.sleep_end - self.sleep_start
        prompt = f"""
        Пожалуйста, проанализируй данные о сне пользователя и предложи дружелюбный и полезный совет по его улучшению.

        Исходные данные:
        — Время отхода ко сну: {self.sleep_start.strftime('%H:%M')}
        — Время пробуждения: {self.sleep_end.strftime('%H:%M')}
        — Продолжительность сна: {self.formatted_sleep_duration()}
        — Оценка качества пробуждения: {self.wake_quality}/3
        — Оценка бодрости после сна: {self.alertness}/3
        — Заметка пользователя: "{self.note or 'Нет заметки'}"

        Учитывай, что идеальный сон состоит из циклов примерно по 90 минут. 
        Обрати на это внимание, если у пользователя сильное отклонение от циклов. 
        Также обрати внимание на пользовательскую оценку лёгкости пробуждения и уровня бодрости в течение дня. 
        Может найдёшь причину, почему оценка низкая.

        Твоя задача — дать краткий (до 3 предложений), вежливый и мотивирующий совет. Используй дружелюбный тон.
        Не повторяй цифры — они есть выше. 
        Сделай акцент на том, что можно попробовать улучшить. 

        Начинай совет сразу, без пояснений.
        """

        self.recommendation = get_sleep_recommendation(prompt)
        print(self.recommendation)

        super().save(*args, **kwargs)

    @property
    def sleep_hours(self):
        if self.sleep_duration:
            return self.sleep_duration.total_seconds() / 3600
        return 0





