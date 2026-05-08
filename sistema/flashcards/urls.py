from django.urls import path
from . import views

app_name = 'flashcards'

urlpatterns = [
    # 1. Lista geral de todos os flashcards (agora filtra por baralhos)
    path('todos/', views.lista_flashcards, name='lista_flashcards'),

    # 2. Criar um novo flashcard (agora precisa do ID do baralho)
    path('novo/<int:baralho_id>/', views.novo_flashcard, name='novo_flashcard'),
    
    # 3. Criar um flashcard a partir da lista geral (sem baralho pré-selecionado)
    path('novo/', views.novo_flashcard, name='novo_flashcard_geral'),

    # 4. Editar um flashcard
    path('editar/<int:pk>/', views.editar_flashcard, name='editar_flashcard'),

    # 5. Excluir um flashcard
    path('excluir/<int:pk>/', views.excluir_flashcard, name='excluir_flashcard'),

    # 6. Iniciar revisão de um baralho específico
    path('revisar/<int:baralho_id>/', views.sessao_revisao, name='sessao_revisao'),

    # 7. Revisão global (estudar tudo)
    path('estudar-hoje/', views.estudar_tudo, name='estudar_tudo'),

    # 8. Registrar a resposta de uma revisão
    path('responder/<int:card_id>/<str:resultado>/', views.registrar_revisao, name='registrar_revisao'),
]