from django.shortcuts import render, get_object_or_404, redirect
from datetime import date, timedelta
from .models import Flashcard, ReviewLog
from subjects.models import Subject # Importante importar o modelo de Matérias

# ABA: MATÉRIAS (Lista as matérias cadastradas)
def lista_materias(request):
    materias = Subject.objects.all()
    return render(request, 'subjects/lista_materias.html', {'materias': materias})

# ABA: FLASHCARDS (Lista todos os flashcards existentes)
def lista_flashcards(request):
    cards = Flashcard.objects.all()
    return render(request, 'flashcards/lista_flashcards.html', {'cards': cards})

# LOGICA DE REVISÃO (O "Coração")
def sessao_revisao(request, materia_id):
    card = Flashcard.objects.filter(
        subject_id=materia_id, 
        next_review__lte=date.today()
    ).first()
    
    if not card:
        return render(request, 'flashcards/sem_cards.html')
        
    return render(request, 'flashcards/revisao.html', {'card': card})

def registrar_revisao(request, card_id, resultado):
    card = get_object_or_404(Flashcard, id=card_id)
    
    acertou = (resultado == 'acerto') # Converte o texto da URL em Booleano
    ReviewLog.objects.create(card=card, success=acertou)

    if acertou:
        card.interval = 1 if card.interval == 0 else card.interval * 2 
    else:
        card.interval = 1

    card.next_review = date.today() + timedelta(days=card.interval)
    card.save()

    # Após responder, volta para a tela de revisão daquela matéria
    return redirect('sessao_revisao', materia_id=card.subject.id)