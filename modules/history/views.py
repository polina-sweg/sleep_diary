from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.views.generic import ListView, DetailView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin

from django.shortcuts import render
from .models import Record
from .forms import RecordEditForm, RecordCreateForm
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.core.exceptions import PermissionDenied


class RecordsListView(LoginRequiredMixin, ListView):
    login_url = '/accounts/login/'
    model = Record
    template_name = 'history/records_list.html'
    context_object_name = 'records'
    paginate_by = 8

    def get_queryset(self):
        return Record.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Главная страница'
        return context


class RecordsDetailView(LoginRequiredMixin, DetailView):
    model = Record
    template_name = 'history/records_detail.html'
    context_object_name = 'record'

    def get_queryset(self):
        return Record.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Возможно стоит добавить title в Record и с помощью регулярок написать там Запись от xx.xx.xxxx
        context['title'] = f"Информация о сне от {self.object.sleep_start.strftime('%d.%m.%Y')}"
        return context

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.user != request.user:
            raise PermissionDenied("У вас нет доступа к этой записи")
        return super().dispatch(request, *args, **kwargs)


@login_required(login_url='/accounts/login/')
def records_list(request):
    records = Record.objects.filter(user=request.user)
    paginator = Paginator(records, per_page=3)
    page_number = request.GET.get('page')
    page_object = paginator.get_page(page_number)
    context = {'page_obj': page_object}
    return render(request, 'history/record_create.html', context)


class RecordCreateView(CreateView):
    model = Record
    form_class = RecordCreateForm
    template_name = 'history/record_create.html'
    success_url = reverse_lazy('home')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class RecordEditView(UpdateView):
    model = Record
    form_class = RecordEditForm
    template_name = 'history/record_edit.html'
    success_url = reverse_lazy('home')


class RecordDeleteView(DeleteView):
    model = Record
    success_url = reverse_lazy('home')
    template_name = 'history/confirm_delete.html'
