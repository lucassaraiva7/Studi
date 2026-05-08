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
    # ALTERAÇÃO: Agora o ForeignKey aponta para Baralho, não para Subject
    baralho = models.ForeignKey(Baralho, on_delete=models.CASCADE, related_name='cards')
    question = models.TextField()
    answer = models.TextField()
    
    # Campos de revisão permanecem os mesmos
    next_review = models.DateField(auto_now_add=True)
    ease_factor = models.FloatField(default=2.5)
    interval = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.baralho.nome} - {self.question[:20]}"

# MODELO ALTERADO: ReviewLog
class ReviewLog(models.Model):
    # Nenhuma alteração aqui, mas é bom confirmar
    card = models.ForeignKey(Flashcard, on_delete=models.CASCADE)
    review_date = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField()