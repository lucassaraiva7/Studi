from django.db import models

# Create your models here.

from django.db import models
from subjects.models import Subject # Importa a matéria para associar [cite: 23]

class Flashcard(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='cards')
    question = models.TextField() # Pergunta do card 
    answer = models.TextField()   # Resposta do card 
    
    # Controle de Revisão Inteligente [cite: 31, 36]
    next_review = models.DateField(auto_now_add=True) # Data da próxima revisão 
    ease_factor = models.FloatField(default=2.5)      # Dificuldade do card
    interval = models.IntegerField(default=0)         # Dias até a próxima revisão
    
    def __str__(self):
        return f"{self.subject.name} - {self.question[:20]}"

class ReviewLog(models.Model):
    """Registra o desempenho para o algoritmo [cite: 34, 35]"""
    card = models.ForeignKey(Flashcard, on_delete=models.CASCADE)
    review_date = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField() # Se o usuário acertou ou errou 