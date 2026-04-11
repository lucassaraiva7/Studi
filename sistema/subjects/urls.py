from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_materias, name='lista_materias'),
    path('nova/', views.nova_materia, name='nova_materia'),
    path('editar/<int:pk>/', views.editar_materia, name='editar_materia'),
    path('excluir/<int:pk>/', views.excluir_materia, name='excluir_materia'),
    path('<int:pk>/', views.materia_detalhes, name='materia_detalhes'),
]