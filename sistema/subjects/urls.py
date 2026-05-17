from django.urls import include, path
from . import views

app_name = 'subjects'

urlpatterns = [
    path('', views.lista_materias, name='lista_materias'),
    path('nova/', views.nova_materia, name='nova_materia'),
    path('editar/<int:pk>/', views.editar_materia, name='editar_materia'),
    path('excluir/<int:pk>/', views.excluir_materia, name='excluir_materia'),
    path('<int:pk>/', views.materia_detalhes, name='materia_detalhes'),
    path('<int:materia_pk>/baralhos/novo/', views.novo_baralho, name='novo_baralho'),
    path('<int:materia_pk>/baralhos/<int:baralho_pk>/', views.baralho_detalhes, name='baralho_detalhes'),
    path('<int:materia_pk>/baralhos/<int:baralho_pk>/excluir/', views.excluir_baralho, name='excluir_baralho'),
    path('<int:materia_pk>/baralhos/<int:baralho_pk>/duplicar/', views.duplicar_baralho, name='duplicar_baralho'),
    path('<int:materia_pk>/baralhos/<int:baralho_pk>/editar/', views.editar_baralho, name='editar_baralho'),
    
]