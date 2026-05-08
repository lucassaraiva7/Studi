from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from datetime import date, timedelta
from .models import Flashcard, ReviewLog, Baralho
from .forms import FlashcardForm
from django.db.models import Q
from urllib.parse import urlparse

@login_required
def lista_flashcards(request):
    # Esta view agora precisa buscar por baralho, não matéria
    query = request.GET.get('q', '')
    baralho_id = request.GET.get('baralho', '')

    cards = Flashcard.objects.filter(baralho__subject__user=request.user)

    if query:
        cards = cards.filter(Q(question__icontains=query) | Q(answer__icontains=query))
    if baralho_id:
        cards = cards.filter(baralho_id=baralho_id)

    baralhos = Baralho.objects.filter(subject__user=request.user)

    return render(request, 'flashcards/lista_flashcards.html', {
        'cards': cards,
        'baralhos': baralhos, # Enviando baralhos para o filtro
        'query': query,
        'baralho_selecionado': baralho_id
    })


@login_required
def novo_flashcard(request, baralho_id=None):
    # Quando acessado sem baralho (rota geral), redireciona para um baralho do usuário.
    if baralho_id is None:
        primeiro_baralho = Baralho.objects.filter(subject__user=request.user).order_by('id').first()
        if not primeiro_baralho:
            return redirect('subjects:lista_materias')
        return redirect('flashcards:novo_flashcard', baralho_id=primeiro_baralho.id)

    baralho = get_object_or_404(Baralho, id=baralho_id, subject__user=request.user)
    
    if request.method == "POST":
        form = FlashcardForm(request.POST, user=request.user)
        # Quando o formulário é criado para um baralho específico, o campo 'baralho' pode
        # não estar presente no POST (pois o template o omite). Neste caso não exigir o campo.
        if 'baralho' in form.fields:
            form.fields['baralho'].required = False

        if form.is_valid():
            card = form.save(commit=False)
            card.baralho = baralho
            card.save()
            return redirect('subjects:baralho_detalhes', materia_pk=baralho.subject.pk, baralho_pk=baralho.pk)
    else:
        # Passa o baralho para o formulário para que ele possa ser usado no template, se necessário
        form = FlashcardForm(initial={'baralho': baralho}, user=request.user)

    return render(request, 'flashcards/form_flashcard.html', {'form': form, 'baralho': baralho})

# Substitua a função editar_flashcard por esta:
@login_required
def editar_flashcard(request, pk):
    card = get_object_or_404(Flashcard, id=pk, baralho__subject__user=request.user)
    baralho_id = card.baralho_id

    if request.method == "POST":
        form = FlashcardForm(request.POST, instance=card, user=request.user)
        # Em edição, o campo 'baralho' não é mostrado no template, portanto não exigir
        if 'baralho' in form.fields:
            form.fields['baralho'].required = False
        if form.is_valid():
            updated = form.save(commit=False)
            # Preserva o vínculo antes de salvar, porque o ModelForm pode limpar a relação.
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
        # Redireciona conforme origem (lista geral ou detalhes do baralho)
        if origem_post == 'geral':
            return redirect('flashcards:lista_flashcards')
        return redirect('subjects:baralho_detalhes', materia_pk=baralho.subject.pk, baralho_pk=baralho.pk)
    return render(request, 'flashcards/confirmar_exclusao_card.html', {'card': card, 'origem': origem})

# --- FUNÇÕES DE REVISÃO CORRIGIDAS ---

def _iniciar_contadores_revisao(request):
    referer = request.META.get('HTTP_REFERER', '')
    if 'revisar' not in referer and 'estudar-hoje' not in referer:
        request.session['acertos'] = 0
        request.session['erros'] = 0

@login_required
def sessao_revisao(request, baralho_id): # Alterado de materia_id para baralho_id
    _iniciar_contadores_revisao(request)
    
    # CORREÇÃO: Filtra por baralho_id, não por subject_id
    card = Flashcard.objects.filter(
        baralho_id=baralho_id,
        baralho__subject__user=request.user,
        next_review__lte=date.today()
    ).order_by('?').first()
    
    if not card:
        acertos = request.session.get('acertos', 0)
        erros = request.session.get('erros', 0)
        return render(request, 'flashcards/resultados_revisao.html', {'acertos': acertos, 'erros': erros})
        
    return render(request, 'flashcards/revisao.html', {'card': card})

@login_required
def estudar_tudo(request):
    _iniciar_contadores_revisao(request)
    
    # CORREÇÃO: A lógica do filtro está correta, pois busca em todos os baralhos do usuário
    card = Flashcard.objects.filter(
        baralho__subject__user=request.user,
        next_review__lte=date.today()
    ).order_by('?').first()
    
    if not card:
        acertos = request.session.get('acertos', 0)
        erros = request.session.get('erros', 0)
        return render(request, 'flashcards/resultados_revisao.html', {'acertos': acertos, 'erros': erros})
        
    return render(request, 'flashcards/revisao.html', {'card': card})

@login_required
def registrar_revisao(request, card_id, resultado):
    card = get_object_or_404(Flashcard, id=card_id, baralho__subject__user=request.user)
    
    if resultado == 'acerto':
        request.session['acertos'] = request.session.get('acertos', 0) + 1
        success = True
    else:
        request.session['erros'] = request.session.get('erros', 0) + 1
        success = False

    if success:
        if card.interval == 0: card.interval = 1
        elif card.interval == 1: card.interval = 6
        else: card.interval = round(card.interval * card.ease_factor)
        card.ease_factor += 0.1
    else:
        card.interval = 0
        card.ease_factor = max(1.3, card.ease_factor - 0.2)

    card.next_review = date.today() + timedelta(days=card.interval)
    card.save()
    # Registrar no log de revisões
    try:
        ReviewLog.objects.create(card=card, success=success)
    except Exception:
        # Falha em criar log não deve bloquear fluxo principal
        pass
    # Garantir que alterações na sessão sejam persistidas
    request.session.modified = True

    # Após registrar, redirecionar para a sessão de revisão do mesmo baralho
    return redirect('flashcards:sessao_revisao', baralho_id=card.baralho.pk)