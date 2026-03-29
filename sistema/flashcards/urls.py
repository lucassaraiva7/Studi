from django.urls import path
from . import views

urlpatterns = [
    path('materias/', views.lista_materias, name='lista_materias'),
    path('todos/', views.lista_flashcards, name='lista_flashcards'),
    path('revisar/<int:materia_id>/', views.sessao_revisao, name='sessao_revisao'),
    path('responder/<int:card_id>/<str:resultado>/', views.registrar_revisao, name='registrar_revisao'),
]