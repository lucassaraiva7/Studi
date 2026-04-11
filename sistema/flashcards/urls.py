from django.urls import path
from . import views

urlpatterns = [
    # GESTÃO (CRUD)
    path('todos/', views.lista_flashcards, name='lista_flashcards'),
    
    # 1. Cadastro Geral (para a aba de Flashcards)
    path('novo/', views.novo_flashcard, name='novo_flashcard_geral'),
    
    # 2. Cadastro Vinculado (dentro da matéria) - Mudei a ordem para evitar conflitos
    path('novo/<int:materia_id>/', views.novo_flashcard, name='novo_flashcard'),
    
    path('editar/<int:pk>/', views.editar_flashcard, name='editar_flashcard'),
    path('excluir/<int:pk>/', views.excluir_flashcard, name='excluir_flashcard'),

    # SESSÕES DE ESTUDO
    path('revisar/<int:materia_id>/', views.sessao_revisao, name='sessao_revisao'),
    path('estudar-hoje/', views.estudar_tudo, name='estudar_tudo'),

    # LÓGICA DO ALGORITMO
    path('responder/<int:card_id>/<str:resultado>/', views.registrar_revisao, name='registrar_revisao'),
]