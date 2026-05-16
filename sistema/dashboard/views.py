from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Q
from datetime import date

# Importando os modelos com base na estrutura real do seu projeto
from subjects.models import Subject  
from flashcards.models import Flashcard, ReviewLog, Baralho

@login_required
def dashboard_estudos(request):
    today = date.today()
    usuario = request.user

    # 1. RESUMO GERAL
    cards_usuario = Flashcard.objects.filter(baralho__subject__user=usuario)
    total_cards = cards_usuario.count()
    cards_pendentes_hoje = cards_usuario.filter(next_review__lte=today).count()
    
    # 2. PROGRESSO POR MATÉRIA E DIFICULDADE (Corrigido para 'baralhos__cards')
    materias_stats = Subject.objects.filter(user=usuario).annotate(
        total_baralhos=Count('baralhos', distinct=True),
        total_cards=Count('baralhos__cards', distinct=True),
        pendentes_hoje=Count(
            'baralhos__cards',
            filter=Q(baralhos__cards__next_review__lte=today),
            distinct=True
        ),
        media_facilidade=Avg('baralhos__cards__ease_factor')
    ).order_by('media_facilidade')  # Matérias mais difíceis aparecem primeiro

    # 3. HISTÓRICO RECENTE DE REVISÕES (Corrigido para usar 'review_date')
    historico_recente = ReviewLog.objects.filter(
        card__baralho__subject__user=usuario
    ).order_by('-review_date')[:5]  # Ordena da mais recente para a mais antiga

    context = {
        'total_cards': total_cards,
        'cards_pendentes_hoje': cards_pendentes_hoje,
        'materias_stats': materias_stats,
        'historico_recente': historico_recente,
    }

    return render(request, 'dashboard/index.html', context)