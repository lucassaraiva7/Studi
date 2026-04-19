from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from datetime import date, timedelta
from .models import Flashcard, ReviewLog
from .forms import FlashcardForm
from subjects.models import Subject
from django.db.models import Q # Import necessário para busca
from urllib.parse import urlparse # Import para checar a URL de origem



@login_required
def lista_flashcards(request):
    query = request.GET.get('q', '')
    materia_id = request.GET.get('materia', '')
    cards = Flashcard.objects.filter(subject__user=request.user)
    if query:
        cards = cards.filter(
            Q(question__icontains=query) | Q(answer__icontains=query)
        )
    if materia_id:
        cards = cards.filter(subject_id=materia_id)
    materias = Subject.objects.filter(user=request.user)
    return render(request, 'flashcards/lista_flashcards.html', {
        'cards': cards,
        'materias': materias,
        'query': query,
        'materia_selecionada': materia_id
    })

@login_required
def novo_flashcard(request, materia_id=None):
    materia = None
    if materia_id:
        materia = get_object_or_404(Subject, id=materia_id, user=request.user)

    if request.method == "POST":
        form = FlashcardForm(request.POST)
        if form.is_valid():
            card = form.save(commit=False)
            # Se a matéria foi passada na URL, ela tem prioridade
            if materia:
                card.subject = materia
            
            # Garante que o card seja associado ao usuário correto através da matéria
            # (Assumindo que o form.cleaned_data['subject'] tem uma matéria do usuário)
            card.save()
            
            # --- CORREÇÃO DA LÓGICA DE REDIRECIONAMENTO ---
            # Em vez de redirecionar, vamos apenas criar um novo formulário em branco
            # para que o usuário possa adicionar outro card em seguida.
            
            # Prepara os dados iniciais para o novo formulário, mantendo a matéria selecionada
            initial_data = {'subject': materia} if materia else {}
            form = FlashcardForm(initial=initial_data)
            # Filtra o dropdown de matérias para o novo formulário
            form.fields['subject'].queryset = Subject.objects.filter(user=request.user)
            
            # Renderiza a página novamente com o formulário limpo
            return render(request, 'flashcards/form_flashcard.html', {
                'form': form,
                'materia': materia,
                'titulo': 'Novo Flashcard',
                'mensagem_sucesso': 'Flashcard criado com sucesso! Adicione o próximo.'
            })
    else:
        # Se não for POST, apenas mostra o formulário em branco pela primeira vez
        initial_data = {'subject': materia} if materia else {}
        form = FlashcardForm(initial=initial_data)
        form.fields['subject'].queryset = Subject.objects.filter(user=request.user)

    return render(request, 'flashcards/form_flashcard.html', {
        'form': form,
        'materia': materia,
        'titulo': 'Novo Flashcard'
    })

@login_required
def editar_flashcard(request, pk):
    card = get_object_or_404(Flashcard, pk=pk, subject__user=request.user)
    
    # Pega a origem da URL (se não tiver, assume que veio da 'materia')
    origem = request.GET.get('origem', 'materia')

    if request.method == "POST":
        form = FlashcardForm(request.POST, instance=card)
        # Pega a origem que veio escondida no formulário
        origem_post = request.POST.get('origem', 'materia')
        
        if form.is_valid():
            form.save()
            # --- LÓGICA DE REDIRECIONAMENTO ---
            if origem_post == 'geral':
                return redirect('lista_flashcards')
            return redirect('materia_detalhes', pk=card.subject.id)
    else:
        form = FlashcardForm(instance=card)
    
    return render(request, 'flashcards/form_flashcard.html', {
        'form': form, 
        'titulo': 'Editar Flashcard',
        'materia': card.subject,
        'origem': origem  # Passa a origem para o template
    })

@login_required
def excluir_flashcard(request, pk):
    card = get_object_or_404(Flashcard, pk=pk, subject__user=request.user)
    
    # Pega a origem da URL para o redirecionamento
    origem = request.GET.get('origem', 'materia')
    materia_id = card.subject.id

    if request.method == "POST":
        card.delete()
        
        # Redirecionamento inteligente após apagar
        if origem == 'geral':
            return redirect('lista_flashcards')
        return redirect('materia_detalhes', pk=materia_id)

    # Passamos a origem para o template de confirmação
    return render(request, 'flashcards/confirmar_exclusao_card.html', {
        'card': card,
        'origem': origem
    })


# --- INÍCIO DAS ALTERAÇÕES ---

def _iniciar_contadores_revisao(request):
    """Verifica se a revisão está começando e zera os contadores."""
    referer = request.META.get('HTTP_REFERER', '')
    # Se não veio de uma página de revisão, é uma nova sessão.
    if 'revisar' not in referer and 'estudar-hoje' not in referer:
        request.session['acertos'] = 0
        request.session['erros'] = 0

@login_required
def sessao_revisao(request, materia_id):
    _iniciar_contadores_revisao(request) # Zera os contadores se for o início

    card = Flashcard.objects.filter(
        subject_id=materia_id,
        subject__user=request.user,
        next_review__lte=date.today()
    ).order_by('?').first() # aleatoriedade
    
    if not card:
        # Se não há mais cards, mostra a página de resultados
        acertos = request.session.get('acertos', 0)
        erros = request.session.get('erros', 0)
        return render(request, 'flashcards/resultados_revisao.html', {
            'acertos': acertos,
            'erros': erros
        })
        
    return render(request, 'flashcards/revisao.html', {'card': card, 'modo': 'materia'})

@login_required
def estudar_tudo(request):
    _iniciar_contadores_revisao(request) # Zera os contadores se for o início

    card = Flashcard.objects.filter(
        subject__user=request.user,
        next_review__lte=date.today()
    ).order_by('?').first()
    
    if not card:
        # Se não há mais cards, mostra a página de resultados
        acertos = request.session.get('acertos', 0)
        erros = request.session.get('erros', 0)
        return render(request, 'flashcards/resultados_revisao.html', {
            'acertos': acertos,
            'erros': erros
        })
        
    return render(request, 'flashcards/revisao.html', {'card': card, 'modo': 'tudo'})

@login_required
def registrar_revisao(request, card_id, resultado):
    card = get_object_or_404(Flashcard, id=card_id, subject__user=request.user)
    
    # Incrementa o contador de acertos ou erros na sessão
    if resultado == 'acerto':
        request.session['acertos'] = request.session.get('acertos', 0) + 1
        success = True
    else:
        request.session['erros'] = request.session.get('erros', 0) + 1
        success = False

    # Lógica do algoritmo de repetição espaçada (SM-2 simplificado)
    if success:
        if card.interval == 0:
            card.interval = 1
        elif card.interval == 1:
            card.interval = 6
        else:
            card.interval = round(card.interval * card.ease_factor)
        
        card.ease_factor += 0.1
    else:
        card.interval = 0 # Reinicia o intervalo
        card.ease_factor = max(1.3, card.ease_factor - 0.2) # Reduz o fator de facilidade

    card.next_review = date.today() + timedelta(days=card.interval)
    card.save()

    # --- CORREÇÃO AQUI ---
    # O nome do campo no modelo é 'card', não 'flashcard'.
    ReviewLog.objects.create(card=card, success=success)
    
    # Redireciona de volta para a mesma URL de onde veio (seja revisão global ou por matéria)
    referer_url = request.META.get('HTTP_REFERER', '/')
    return redirect(referer_url)