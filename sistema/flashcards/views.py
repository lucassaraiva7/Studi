from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required # Importante!
from datetime import date, timedelta
from .models import Flashcard, ReviewLog
from .forms import FlashcardForm
from subjects.models import Subject

@login_required
def lista_flashcards(request):
    # Pega os parâmetros da URL (ex: ?q=python&materia=1)
    query = request.GET.get('q', '')
    materia_id = request.GET.get('materia', '')

    # Começa com todos os cards do usuário
    cards = Flashcard.objects.filter(subject__user=request.user)

    # Aplica a busca por texto (Pergunta ou Resposta)
    if query:
        cards = cards.filter(
            Q(question__icontains=query) | Q(answer__icontains=query)
        )

    # Aplica o filtro por Matéria
    if materia_id:
        cards = cards.filter(subject_id=materia_id)

    # Busca as matérias para preencher o select do filtro
    materias = Subject.objects.filter(user=request.user)

    return render(request, 'flashcards/lista_flashcards.html', {
        'cards': cards,
        'materias': materias,
        'query': query,
        'materia_selecionada': materia_id
    })
    

# 2. CADASTRAR
@login_required
def novo_flashcard(request, materia_id):
    materia = get_object_or_404(Subject, id=materia_id, user=request.user)
    
    if request.method == "POST":
        form = FlashcardForm(request.POST)
        if form.is_valid():
            card = form.save(commit=False)
            card.subject = materia 
            card.save()
            return redirect('materia_detalhes', pk=materia.id)
    else:
        # Passamos a matéria inicial, mas no template você pode esconder esse campo
        form = FlashcardForm(initial={'subject': materia})
    
    return render(request, 'flashcards/form_flashcard.html', {
        'form': form,
        'materia': materia,
        'titulo': f'Novo Flashcard para {materia.name}'
    })

# 3. EDITAR
@login_required
def editar_flashcard(request, pk):
    card = get_object_or_404(Flashcard, pk=pk, subject__user=request.user)
    
    # 1. Pega a origem da URL (se não tiver, assume que veio da 'materia')
    origem = request.GET.get('origem', 'materia')

    if request.method == "POST":
        form = FlashcardForm(request.POST, instance=card)
        # 2. Pega a origem que veio escondida no formulário
        origem = request.POST.get('origem', 'materia')
        
        if form.is_valid():
            form.save()
            # 3. Redirecionamento Inteligente
            if origem == 'geral':
                return redirect('lista_flashcards')
            return redirect('materia_detalhes', pk=card.subject.id)
    else:
        form = FlashcardForm(instance=card)
    
    return render(request, 'flashcards/form_flashcard.html', {
        'form': form, 
        'titulo': 'Editar Flashcard',
        'materia': card.subject,
        'origem': origem # Passa a origem para o template
    })

# EXCLUIR
@login_required
def excluir_flashcard(request, pk):
    # Usamos filter().first() para evitar o erro 404 caso o card já tenha sido apagado
    card = Flashcard.objects.filter(pk=pk, subject__user=request.user).first()
    
    # Se o card não existe (já foi apagado), volta para onde o usuário estava
    origem = request.GET.get('origem', 'materia')
    if not card:
        if origem == 'geral':
            return redirect('lista_flashcards')
        return redirect('lista_materias') # Ou uma página padrão segura

    materia_id = card.subject.id

    if request.method == "POST":
        origem = request.POST.get('origem', 'materia')
        card.delete()
        
        # Redirecionamento após apagar
        if origem == 'geral':
            return redirect('lista_flashcards')
        return redirect('materia_detalhes', pk=materia_id)

    # Passamos a origem para o template de confirmação
    return render(request, 'flashcards/confirmar_exclusao_card.html', {
        'card': card,
        'origem': origem
    })

# 5. REVISÃO POR MATÉRIA
@login_required
def sessao_revisao(request, materia_id):
    # Adicionado order_by('?') para aleatoriedade ou por data
    card = Flashcard.objects.filter(
        subject_id=materia_id,
        subject__user=request.user,
        next_review__lte=date.today()
    ).first()
    
    if not card:
        return render(request, 'flashcards/sem_cards.html', {'materia_id': materia_id})
        
    return render(request, 'flashcards/revisao.html', {'card': card, 'modo': 'materia'})

# 6. REVISÃO GLOBAL
@login_required
def estudar_tudo(request):
    card = Flashcard.objects.filter(
        subject__user=request.user,
        next_review__lte=date.today()
    ).order_by('?').first()
    
    if not card:
        return render(request, 'flashcards/sem_cards.html')
        
    return render(request, 'flashcards/revisao.html', {'card': card, 'modo': 'tudo'})

# 7. REGISTRAR REVISÃO
@login_required
def registrar_revisao(request, card_id, resultado):
    card = get_object_or_404(Flashcard, id=card_id, subject__user=request.user)
    
    acertou = (resultado == 'acerto')
    ReviewLog.objects.create(card=card, success=acertou)

    # Lógica de espaçamento simples
    if acertou:
        card.interval = 1 if card.interval == 0 else card.interval * 2
    else:
        card.interval = 1

    card.next_review = date.today() + timedelta(days=card.interval)
    card.save()

    # Melhoria: Se houver um parâmetro 'proximo', redireciona para a view de origem
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('lista_flashcards')