from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm

def cadastrar_usuario(request):
    # Se o usuário enviou o formulário (clicou no botão de salvar)
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()  # Salva o usuário no banco com senha criptografada
            username = form.cleaned_data.get('username')
            messages.success(request, f'Conta criada com sucesso para {username}! Faça o login.')
            return redirect('login')  # Redireciona para a tela de login (vamos criar depois)
    else:
        # Se o usuário está apenas acessando a página, exibe o formulário vazio
        form = UserCreationForm()
        
    return render(request, 'usuarios/cadastro.html', {'form': form})