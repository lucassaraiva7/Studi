from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    # Rota do painel de administracao padrao
    path('admin/', admin.site.urls),

    # Rota da raiz - Carrega a Landing Page
    path('', TemplateView.as_view(template_name='landing.html'), name='landing'),

    # Rota do Dashboard - Painel interno pos-login
    path('dashboard/', include('dashboard.urls')),

    # Rota das materias
    path('subjects/', include('subjects.urls')),

    # Rota dos flashcards
    path('flashcards/', include('flashcards.urls')),

    # Rota do gerador IA
    path('generator/', include('generator.urls')),

    # Rotas de autenticacao e perfil
    path('auth/', include('usuarios.urls')),
]