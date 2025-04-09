from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic import FormView
from .forms import SignUpForm, LoginForm, ProfileForm
from django.contrib import messages


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно! Добро пожаловать!')
            return redirect('profile')
        else:
            messages.error(request, 'Ошибка при регистрации. Пожалуйста, попробуйте снова.')
    else:
        form = SignUpForm()
    return render(request, 'system/signup.html', {'form': form})


class LoginView(FormView):
    form_class = LoginForm
    template_name = 'system/login.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        login(self.request, form.get_user())
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Неверный email или пароль.')
        return super().form_invalid(form)

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        return next_url or str(self.success_url)


def user_logout(request):
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы.')
    return redirect('login')


@login_required(login_url='/accounts/login/')
def profile(request):
    user = request.user
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ваш профиль был обновлен!')
            return redirect('profile')
        else:
            messages.error(request, 'Не удалось обновить профиль. Пожалуйста, попробуйте еще раз.')
    else:
        form = ProfileForm(instance=user)
    return render(request, 'system/profile.html', {'form': form})
