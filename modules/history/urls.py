from django.urls import path
from .views import (RecordsListView, RecordsDetailView, records_list,
                    RecordCreateView, RecordEditView, RecordDeleteView)


urlpatterns = [
    path('', RecordsListView.as_view(), name='home'),
    path('history/<int:pk>', RecordsDetailView.as_view(), name='records_detail'),
    path('records/', records_list, name='records_by_page'),
    path('create/', RecordCreateView.as_view(), name='record_create'),
    path('<int:pk>/edit/', RecordEditView.as_view(), name='record_edit'),
    path('record/delete/<int:pk>/', RecordDeleteView.as_view(), name='record_delete'),

]