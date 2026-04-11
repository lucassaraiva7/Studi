from django import forms
from .models import Flashcard
from subjects.models import Subject

class FlashcardForm(forms.ModelForm):
    class Meta:
        model = Flashcard
        fields = ['subject', 'question', 'answer']
        labels = {'subject': 'Matéria', 'question': 'Pergunta', 'answer': 'Resposta'}

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # Só mostra as matérias que o usuário logado criou
            self.fields['subject'].queryset = Subject.objects.filter(user=user)