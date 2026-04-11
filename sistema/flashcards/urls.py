from django.urls import path
from . import views

urlpatterns = [
    # GESTÃO (CRUD)
    path('todos/', views.lista_flashcards, name='lista_flashcards'),
    path('novo/', views.novo_flashcard, name='novo_flashcard'),
    path('editar/<int:pk>/', views.editar_flashcard, name='editar_flashcard'),
    path('excluir/<int:pk>/', views.excluir_flashcard, name='excluir_flashcard'),

    # SESSÕES DE ESTUDO
    # Estudar uma matéria específica
    path('revisar/<int:materia_id>/', views.sessao_revisao, name='sessao_revisao'),
    # Estudar TUDO que está atrasado (Geral)
    path('estudar-hoje/', views.estudar_tudo, name='estudar_tudo'),

    # LÓGICA DO ALGORITMO
    path('responder/<int:card_id>/<str:resultado>/', views.registrar_revisao, name='registrar_revisao'),
    
    path('novo/<int:materia_id>/', views.novo_flashcard, name='novo_flashcard'),
]