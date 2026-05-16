from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Q
from datetime import date, timedelta

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
    
    # 2. PROGRESSO POR MATÉRIA E DIFICULDADE
    materias_stats = Subject.objects.filter(user=usuario).annotate(
        total_baralhos=Count('baralhos', distinct=True),
        total_cards=Count('baralhos__cards', distinct=True),
        pendentes_hoje=Count(
            'baralhos__cards',
            filter=Q(baralhos__cards__next_review__lte=today),
            distinct=True
        ),
        media_facilidade=Avg('baralhos__cards__ease_factor')
    ).order_by('media_facilidade')

    # 3. HISTÓRICO RECENTE (Lista lateral)
    historico_recente = ReviewLog.objects.filter(
        card__baralho__subject__user=usuario
    ).order_by('-review_date')[:5]

    # 4. LÓGICA DO GRÁFICO (Últimos 7 dias)
    data_limite = today - timedelta(days=6)
    logs_periodo = ReviewLog.objects.filter(
        card__baralho__subject__user=usuario,
        review_date__date__gte=data_limite
    ).values('review_date__date').annotate(
        total=Count('id'),
        facil=Count('id', filter=Q(grade='facil'))
    ).order_by('review_date__date')

    # Monta um dicionário para garantir que dias sem revisão também apareçam com 0
    dados_grafico = {}
    for i in range(6, -1, -1):
        dia = today - timedelta(days=i)
        dados_grafico[dia] = {'total': 0, 'facil': 0}

    for log in logs_periodo:
        log_date = log['review_date__date']
        if log_date in dados_grafico:
            dados_grafico[log_date] = {'total': log['total'], 'facil': log['facil']}

    # Separa as listas para enviar ao Chart.js no frontend
    chart_labels = [dia.strftime('%d/%m') for dia in dados_grafico.keys()]
    chart_totals = [info['total'] for info in dados_grafico.values()]
    chart_facil = [info['facil'] for info in dados_grafico.values()]

    context = {
        'total_cards': total_cards,
        'cards_pendentes_hoje': cards_pendentes_hoje,
        'materias_stats': materias_stats,
        'historico_recente': historico_recente,
        # Dados do gráfico:
        'chart_labels': chart_labels,
        'chart_totals': chart_totals,
        'chart_facil': chart_facil,
    }

    return render(request, 'dashboard/index.html', context)