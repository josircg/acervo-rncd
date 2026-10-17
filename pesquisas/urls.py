from django.urls import path

from . import views

app_name = 'pesquisas'

urlpatterns = [
    path('', views.document_search, name='index'),
    path('documentos/<int:pk>/abrir/', views.document_open, name='document_open'),
]
