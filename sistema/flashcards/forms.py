# Em sistema/flashcards/forms.py

from django import forms
from .models import Flashcard, Baralho
from subjects.models import Subject

class FlashcardForm(forms.ModelForm):
    class Meta:
        model = Flashcard
        fields = ['baralho', 'question', 'answer']
        widgets = {
            'question': forms.Textarea(attrs={'rows': 3}),
            'answer': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        # Remove 'user' de kwargs antes de chamar o super construtor
        user = kwargs.pop('user', None)
        super(FlashcardForm, self).__init__(*args, **kwargs)
        
        if user:
            # Filtra o queryset do campo 'baralho' para mostrar apenas os baralhos do usuário logado.
            self.fields['baralho'].queryset = Baralho.objects.filter(subject__user=user)
        # Se o formulário foi criado com uma instância (edição) ou com initial 'baralho',
        # não forçar o campo como obrigatório, pois em templates ele pode estar oculto.
        if 'baralho' in self.fields and (self.instance and self.instance.pk or self.initial.get('baralho')):
            self.fields['baralho'].required = False

class BaralhoForm(forms.ModelForm):
    class Meta:
        model = Baralho
        fields = ['nome', 'descricao']