from django.db import models
from subjects.models import Subject

# NOVO MODELO: Baralho
class Baralho(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='baralhos')
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.nome

# MODELO ALTERADO: Flashcard
class Flashcard(models.Model):
    baralho = models.ForeignKey(Baralho, on_delete=models.CASCADE, related_name='cards')
    question = models.TextField()
    answer = models.TextField()
    
    # Campos de revisão técnica
    next_review = models.DateField(auto_now_add=True)
    ease_factor = models.FloatField(default=2.5) # O "EF" do algoritmo
    interval = models.IntegerField(default=0)    # Intervalo em dias
    repetitions = models.IntegerField(default=0) # Contagem de sucessos seguidos

    def __str__(self):
        return f"{self.baralho.nome} - {self.question[:20]}"


class ReviewLog(models.Model):
    card = models.ForeignKey(Flashcard, on_delete=models.CASCADE)
    review_date = models.DateTimeField(auto_now_add=True)
    grade = models.CharField(max_length=10, default='medio') 

    def __str__(self):
        # Usando .get para evitar erros se a questão for vazia
        question_display = self.card.question[:10] if self.card.question else "Sem pergunta"
        return f"{question_display} - {self.grade} em {self.review_date}"