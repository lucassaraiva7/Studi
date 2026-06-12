from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CadastroRobustoForm # Importa o novo formulário

def cadastrar_usuario(request):
    if request.method == 'POST':
        form = CadastroRobustoForm(request.POST) # Usa o novo formulário aqui
        if form.is_valid():
            form.save() # O Django já salva nome, sobrenome e email no banco automaticamente
            username = form.cleaned_data.get('username')
            messages.success(request, f'Conta criada com sucesso para {username}!')
            return redirect('login')
    else:
        form = CadastroRobustoForm() # Usa o novo formulário aqui também
        
    return render(request, 'usuarios/cadastro.html', {'form': form})