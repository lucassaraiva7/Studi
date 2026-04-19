from django.shortcuts import render, redirect, get_object_or_404
from .models import Subject
from .forms import SubjectForm
from flashcards.models import Flashcard 

def lista_materias(request):
    materias = Subject.objects.all()
    return render(request, 'subjects/lista_materias.html', {'materias': materias})

def nova_materia(request):
    if request.method == "POST":
        form = SubjectForm(request.POST)
        if form.is_valid():
            materia = form.save(commit=False)
            materia.user = request.user
            materia.save()
            return redirect('lista_materias')
    else:
        form = SubjectForm()
    return render(request, 'subjects/form_materia.html', {'form': form, 'titulo': 'Nova Matéria'})


# 2. EDITAR
def editar_materia(request, pk):
    materia = get_object_or_404(Subject, pk=pk, user=request.user)
    if request.method == "POST":
        form = SubjectForm(request.POST, instance=materia)
        if form.is_valid():
            form.save()
            return redirect('lista_materias')
    else:
        form = SubjectForm(instance=materia)
    return render(request, 'subjects/form_materia.html', {'form': form, 'titulo': 'Editar Matéria'})

# 3. EXCLUIR
def excluir_materia(request, pk):
    materia = get_object_or_404(Subject, pk=pk, user=request.user)
    if request.method == "POST":
        materia.delete()
        return redirect('lista_materias')
    return render(request, 'subjects/confirmar_exclusao.html', {'materia': materia})

from flashcards.models import Flashcard # Importe o modelo de Flashcard

def materia_detalhes(request, pk):
    # Busca a matéria
    materia = get_object_or_404(Subject, pk=pk, user=request.user)
    # Busca apenas os cards dessa matéria
    cards = Flashcard.objects.filter(subject=materia)
    
    return render(request, 'subjects/materia_detalhes.html', {
        'materia': materia,
        'cards': cards
    })