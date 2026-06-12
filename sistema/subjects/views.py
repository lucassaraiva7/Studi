from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Subject
from .forms import SubjectForm
from flashcards.models import Baralho 
from flashcards.forms import BaralhoForm 
from flashcards.models import Flashcard 
@login_required
def lista_materias(request):
    # CORREÇÃO: Filtra as matérias para mostrar apenas as do usuário logado.
    materias = Subject.objects.filter(user=request.user)
    return render(request, 'subjects/lista_materias.html', {'materias': materias})

@login_required
def nova_materia(request):
    if request.method == "POST":
        form = SubjectForm(request.POST)
        if form.is_valid():
            materia = form.save(commit=False)
            materia.user = request.user
            materia.save()
            return redirect('subjects:lista_materias')
    else:
        form = SubjectForm()
    return render(request, 'subjects/form_materia.html', {'form': form, 'titulo': 'Nova Matéria'})

@login_required
def editar_materia(request, pk):
    materia = get_object_or_404(Subject, pk=pk, user=request.user)
    if request.method == "POST":
        form = SubjectForm(request.POST, instance=materia)
        if form.is_valid():
            form.save()
            return redirect('subjects:lista_materias')
    else:
        form = SubjectForm(instance=materia)
    return render(request, 'subjects/form_materia.html', {'form': form, 'titulo': 'Editar Matéria'})

@login_required
def excluir_materia(request, pk):
    materia = get_object_or_404(Subject, pk=pk, user=request.user)
    if request.method == "POST":
        materia.delete()
        return redirect('subjects:lista_materias')
    return render(request, 'subjects/confirmar_exclusao.html', {'materia': materia})

@login_required
def materia_detalhes(request, pk):
    materia = get_object_or_404(Subject, pk=pk, user=request.user)
    baralhos = Baralho.objects.filter(subject=materia)
    # Todos os flashcards pertencentes aos baralhos desta matéria
    cards = Flashcard.objects.filter(baralho__subject=materia)
    context = {
        'materia': materia,
        'baralhos': baralhos 
        , 'cards': cards
    }
    return render(request, 'subjects/materia_detalhes.html', context)

@login_required
def novo_baralho(request, materia_pk):
    materia = get_object_or_404(Subject, pk=materia_pk, user=request.user)
    if request.method == "POST":
        form = BaralhoForm(request.POST)
        if form.is_valid():
            baralho = form.save(commit=False)
            baralho.subject = materia
            baralho.save()
            return redirect('subjects:materia_detalhes', pk=materia.pk)
    else:
        form = BaralhoForm()
    
    return render(request, 'subjects/form_baralho.html', {
        'form': form,
        'materia': materia,
        'titulo': 'Novo Baralho'
    })


@login_required
def editar_baralho(request, materia_pk, baralho_pk):
    materia = get_object_or_404(Subject, pk=materia_pk, user=request.user)
    baralho = get_object_or_404(Baralho, pk=baralho_pk, subject=materia)
    if request.method == 'POST':
        form = BaralhoForm(request.POST, instance=baralho)
        if form.is_valid():
            form.save()
            return redirect('subjects:baralho_detalhes', materia_pk=materia.pk, baralho_pk=baralho.pk)
    else:
        form = BaralhoForm(instance=baralho)
    return render(request, 'subjects/form_baralho.html', {'form': form, 'materia': materia, 'titulo': 'Editar Baralho'})

@login_required
def baralho_detalhes(request, materia_pk, baralho_pk):
    baralho = get_object_or_404(Baralho, pk=baralho_pk, subject__pk=materia_pk, subject__user=request.user)
    flashcards = Flashcard.objects.filter(baralho=baralho)
    context = {
        'baralho': baralho,
        'flashcards': flashcards,
    }
    return render(request, 'subjects/baralho_detalhes.html', context)


@login_required
def duplicar_baralho(request, materia_pk, baralho_pk):
    origem = get_object_or_404(Baralho, pk=baralho_pk, subject__pk=materia_pk, subject__user=request.user)
    # Cria cópia do baralho
    novo_nome = f"Cópia de {origem.nome}"
    novo_baralho = Baralho.objects.create(subject=origem.subject, nome=novo_nome, descricao=origem.descricao)

    # Duplica flashcards
    cards = Flashcard.objects.filter(baralho=origem)
    for c in cards:
        Flashcard.objects.create(
            baralho=novo_baralho,
            question=c.question,
            answer=c.answer,
            next_review=c.next_review,
            ease_factor=c.ease_factor,
            interval=c.interval
        )

    return redirect('subjects:baralho_detalhes', materia_pk=novo_baralho.subject.pk, baralho_pk=novo_baralho.pk)

# Adicione ao final de sistema/subjects/views.py

@login_required
def excluir_baralho(request, materia_pk, baralho_pk):
    baralho = get_object_or_404(Baralho, pk=baralho_pk, subject__pk=materia_pk, subject__user=request.user)
    if request.method == 'POST':
        materia_id = baralho.subject.pk
        baralho.delete()
        return redirect('subjects:materia_detalhes', pk=materia_id)
    return render(request, 'subjects/confirmar_exclusao_baralho.html', {'baralho': baralho})
