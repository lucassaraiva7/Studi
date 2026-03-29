from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import User

class Subject(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # Vincula ao usuário 
    name = models.CharField(max_length=100) # Nome da matéria (ex: Física 3) 
    created_at = models.DateTimeField(auto_now_add=True)
    color = models.CharField(max_length=7, default="#808080")

    def __str__(self):
        return self.name