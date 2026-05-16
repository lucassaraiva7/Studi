from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from datetime import date, timedelta
from .models import Flashcard, ReviewLog, Baralho
from .forms import FlashcardForm
from django.db.models import Q
from urllib.parse import urlparse

@login_required
def lista_flashcards(request):
    query = request.GET.get('q', '')
    baralho_id = request.GET.get('baralho', '')

    # 1. Começamos filtrando pelos cards do usuário logado
    cards = Flashcard.objects.filter(baralho__subject__user=request.user)

    # 2. Filtro de busca (Lupa)
    if query:
        cards = cards.filter(Q(question__icontains=query) | Q(answer__icontains=query))
    
    # 3. Filtro por Baralho
    if baralho_id:
        cards = cards.filter(baralho_id=baralho_id)

    # 4. Ordenação: Mostra primeiro os cards que precisam ser revisados antes
    cards = cards.order_by('next_review')

    baralhos = Baralho.objects.filter(subject__user=request.user)

    return render(request, 'flashcards/lista_flashcards.html', {
        'cards': cards,
        'baralhos': baralhos,
        'query': query,
        'baralho_selecionado': baralho_id,
        'today': date.today()  # Envia a data de hoje para o template
    })

@login_required
def novo_flashcard(request, baralho_id=None):
    if baralho_id is None:
        primeiro_baralho = Baralho.objects.filter(subject__user=request.user).order_by('id').first()
        if not primeiro_baralho:
            return redirect('subjects:lista_materias')
        return redirect('flashcards:novo_flashcard', baralho_id=primeiro_baralho.id)

    baralho = get_object_or_404(Baralho, id=baralho_id, subject__user=request.user)
    
    if request.method == "POST":
        form = FlashcardForm(request.POST, user=request.user)
        if 'baralho' in form.fields:
            form.fields['baralho'].required = False

        if form.is_valid():
            card = form.save(commit=False)
            card.baralho = baralho
            card.save()
            return redirect('subjects:baralho_detalhes', materia_pk=baralho.subject.pk, baralho_pk=baralho.pk)
    else:
        form = FlashcardForm(initial={'baralho': baralho}, user=request.user)

    return render(request, 'flashcards/form_flashcard.html', {'form': form, 'baralho': baralho})

@login_required
def editar_flashcard(request, pk):
    card = get_object_or_404(Flashcard, id=pk, baralho__subject__user=request.user)
    baralho_id = card.baralho_id

    if request.method == "POST":
        form = FlashcardForm(request.POST, instance=card, user=request.user)
        if 'baralho' in form.fields:
            form.fields['baralho'].required = False
        if form.is_valid():
            updated = form.save(commit=False)
            updated.baralho_id = baralho_id
            updated.save()
            return redirect('subjects:baralho_detalhes', materia_pk=updated.baralho.subject.pk, baralho_pk=baralho_id)
    else:
        form = FlashcardForm(instance=card, user=request.user)

    return render(request, 'flashcards/form_flashcard.html', {'form': form, 'card': card, 'baralho': get_object_or_404(Baralho, pk=baralho_id, subject__user=request.user)})

@login_required
def excluir_flashcard(request, pk):
    card = get_object_or_404(Flashcard, pk=pk, baralho__subject__user=request.user)
    baralho = card.baralho
    origem = request.GET.get('origem', '')
    if request.method == "POST":
        origem_post = request.POST.get('origem', '')
        card.delete()
        if origem_post == 'geral':
            return redirect('flashcards:lista_flashcards')
        return redirect('subjects:baralho_detalhes', materia_pk=baralho.subject.pk, baralho_pk=baralho.pk)
    return render(request, 'flashcards/confirmar_exclusao_card.html', {'card': card, 'origem': origem})


# --- FUNÇÕES DE REVISÃO ATUALIZADAS ---

def _iniciar_contadores_revisao(request):
    referer = request.META.get('HTTP_REFERER', '')
    if 'revisar' not in referer and 'estudar-hoje' not in referer:
        request.session['facil'] = 0
        request.session['medio'] = 0
        request.session['dificil'] = 0

@login_required
def sessao_revisao(request, baralho_id):
    _iniciar_contadores_revisao(request)
    
    # INDICA QUE ESTAMOS A REVISAR APENAS UM BARALHO ESPECÍFICO
    request.session['modo_global'] = False
    
    card = Flashcard.objects.filter(
        baralho_id=baralho_id,
        baralho__subject__user=request.user,
        next_review__lte=date.today()
    ).order_by('?').first()
    
    if not card:
        facil = request.session.get('facil', 0)
        medio = request.session.get('medio', 0)
        dificil = request.session.get('dificil', 0)
        total = facil + medio + dificil
        
        if total > 0:
            context = {'facil': facil, 'medio': medio, 'dificil': dificil, 'total': total}
            return render(request, 'flashcards/resultados_revisao.html', context)
        else:
            return render(request, 'flashcards/sem_cards_para_revisar.html')
        
    return render(request, 'flashcards/revisao.html', {'card': card})

@login_required
def estudar_tudo(request):
    _iniciar_contadores_revisao(request)
    
    # INDICA AO SISTEMA QUE ESTAMOS NO MODO DE REVISÃO GLOBAL (Sessão Única)
    request.session['modo_global'] = True
    
    card = Flashcard.objects.filter(
        baralho__subject__user=request.user,
        next_review__lte=date.today()
    ).order_by('?').first()
    
    if not card:
        # Quando terminarem todos os cards de todas as matérias, desliga a flag
        request.session['modo_global'] = False
        
        facil = request.session.get('facil', 0)
        medio = request.session.get('medio', 0)
        dificil = request.session.get('dificil', 0)
        total = facil + medio + dificil
        
        if total > 0:
            context = {'facil': facil, 'medio': medio, 'dificil': dificil, 'total': total}
            return render(request, 'flashcards/resultados_revisao.html', context)
        else:
            return render(request, 'flashcards/sem_cards_para_revisar.html')
        
    return render(request, 'flashcards/revisao.html', {'card': card})


@login_required
def registrar_revisao(request, card_id, resultado):
    card = get_object_or_404(Flashcard, id=card_id, baralho__subject__user=request.user)
    
    # Incrementa o contador na sessão
    request.session[resultado] = request.session.get(resultado, 0) + 1
    
    # Mapeamento de notas para o algoritmo
    if resultado == 'facil':
        grade = 5
    elif resultado == 'medio':
        grade = 4
    else:
        grade = 3

    # --- LÓGICA SM-2 ---
    if card.repetitions == 0:
        if grade == 5: card.interval = 4
        elif grade == 4: card.interval = 2
        else: card.interval = 1
        card.repetitions = 1
    elif card.repetitions == 1:
        if grade == 5: card.interval = 10
        else: card.interval = 6
        card.repetitions = 2
    else:
        if grade == 5: card.interval = round(card.interval * card.ease_factor * 1.2)
        elif grade == 4: card.interval = round(card.interval * card.ease_factor)
        else: card.interval = round(card.interval * 1.2)
        card.repetitions += 1

    card.ease_factor += (0.1 - (5 - grade) * (0.08 + (5 - grade) * 0.02))
    if card.ease_factor < 1.3: card.ease_factor = 1.3

    card.next_review = date.today() + timedelta(days=card.interval)
    card.save()

    ReviewLog.objects.create(card=card, grade=resultado)
    request.session.modified = True

    # --- REDIRECIONAMENTO INTELIGENTE (RESOLVE O TEU PROBLEMA) ---
    if request.session.get('modo_global'):
        # Se veio pelo botão "Revisar Tudo", mantém-se no loop global de todas as matérias
        return redirect('flashcards:estudar_tudo')
    else:
        # Se entrou por um baralho individual, continua focado apenas nesse baralho
        return redirect('flashcards:sessao_revisao', baralho_id=card.baralho.pk)