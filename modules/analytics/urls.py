from django.urls import path
from .views import SleepAnalyticsView

urlpatterns = [
    path('', SleepAnalyticsView.as_view(), name='analytics_dashboard'),
]