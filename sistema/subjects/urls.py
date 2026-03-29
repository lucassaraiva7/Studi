from django.urls import path
from flashcards import views # Importamos as views do flashcards já que você unificou a lógica lá

urlpatterns = [
    # Esta é a rota que a sua aba "Matérias" vai usar
    path('', views.lista_materias, name='lista_materias'),
]