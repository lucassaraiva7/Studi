from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CriarComIAForm
from .services import extrair_texto_pdf, gerar_flashcards_com_ia

# IMPORTS CORRIGIDOS:
from subjects.models import Subject  
from flashcards.models import Baralho, Flashcard

@login_required
def criar_com_ia(request):
    if request.method == 'POST':
        # Passamos o 'user' para o formulário validar e filtrar as matérias corretamente
        form = CriarComIAForm(request.POST, request.FILES, user=request.user)
        
        if form.is_valid():
            nome_baralho = form.cleaned_data['nome_baralho']
            materia = form.cleaned_data['materia']
            arquivo_pdf = request.FILES['arquivo_pdf']
            
            try:
                # 1. Extrai o texto do PDF carregado
                texto_extraido = extrair_texto_pdf(arquivo_pdf)
                
                # Validação extra caso o PDF seja apenas imagens/scans sem texto legível
                if len(texto_extraido.strip()) < 50:
                    raise ValueError("O PDF parece não conter texto legível (pode ser uma imagem digitalizada). Tente outro arquivo.")
                
                # 2. Envia para a API do Gemini processar e gerar a lista de perguntas/respostas
                lista_cards = gerar_flashcards_com_ia(texto_extraido)
                
                # 3. Cria o objeto do novo Baralho no banco de dados
                novo_baralho = Baralho.objects.create(
                    nome=nome_baralho,
                    subject=materia
                )
                
                # 4. Faz um loop salvando cada flashcard gerado pela IA
                for card in lista_cards:
                    Flashcard.objects.create(
                        baralho=novo_baralho,
                        question=card['question'],
                        answer=card['answer']
                    )
                
                # Mensagem de sucesso flutuante para o usuário
                messages.success(request, f"Sucesso! IA gerou {len(lista_cards)} flashcards para o baralho '{nome_baralho}'.")
                
                # 5. Redireciona o usuário direto para a tela do baralho criado
                return redirect('subjects:baralho_detalhes', materia_pk=materia.pk, baralho_pk=novo_baralho.pk)
                
            except Exception as e:
                # Se algo falhar (API fora do ar, PDF corrompido, etc), captura o erro e exibe na tela
                messages.error(request, f"Erro ao gerar flashcards: {str(e)}")
    else:
        form = CriarComIAForm(user=request.user)
        
    return render(request, 'generator/criar_com_ia.html', {'form': form})