from django import forms
from subjects.models import Subject  # Importa o modelo de Matérias do seu outro app

class CriarComIAForm(forms.Form):
    nome_baralho = forms.CharField(
        label="Nome do Novo Baralho",
        max_length=100,
        help_text="Dê um nome claro para o baralho que a IA vai criar."
    )
    
    materia = forms.ModelChoiceField(
        label="Vincular à Matéria",
        queryset=Subject.objects.none(),  # Começa vazio por segurança
        empty_label="Selecione a matéria..."
    )
    
    arquivo_pdf = forms.FileField(
        label="Arquivo PDF de Estudo",
        help_text="Selecione um arquivo PDF de até 10MB."
    )

    def __init__(self, *args, **kwargs):
        # Captura o usuário logado passado pela View para filtrar as matérias
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filtra as matérias para mostrar apenas as que pertencem ao usuário atual
        if user:
            self.fields['materia'].queryset = Subject.objects.filter(user=user)

    def clean_arquivo_pdf(self):
        """
        Validação personalizada para garantir que o arquivo é um PDF 
        e que ele respeita o limite de 10MB.
        """
        arquivo = self.cleaned_data.get('arquivo_pdf')
        
        if arquivo:
            # 1. Valida a extensão do arquivo
            if not arquivo.name.endswith('.pdf'):
                raise forms.ValidationError("Formato inválido! Por favor, envie apenas arquivos .pdf")
            
            # 2. Valida o tamanho máximo (10MB = 10 * 1024 * 1024 bytes)
            limite_tamanho = 10 * 1024 * 1024
            if arquivo.size > limite_tamanho:
                raise forms.ValidationError("Arquivo muito grande! O limite máximo permitido é de 10MB.")
                
        return arquivo