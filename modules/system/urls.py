from django.urls import path
from .views import signup, LoginView, user_logout, profile

urlpatterns = [
    path('signup/', signup, name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', user_logout, name='logout'),
    path('profile/', profile, name='profile'),
]