from django.urls import path
from . import views

app_name = 'generator'

urlpatterns = [
    # Rota para a tela de criação com IA
    path('criar-com-ia/', views.criar_com_ia, name='criar_com_ia'),
]