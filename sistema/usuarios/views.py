from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required  
from django.contrib.auth import logout                     
from .forms import CadastroRobustoForm 

# ========================================================
# 1. VIEW DE CADASTRO 
# ========================================================
def cadastrar_usuario(request):
    if request.method == 'POST':
        form = CadastroRobustoForm(request.POST) 
        if form.is_valid():
            form.save() 
            username = form.cleaned_data.get('username')
            messages.success(request, f'Conta criada com sucesso para {username}!')
            return redirect('login')
    else:
        form = CadastroRobustoForm() 
        
    return render(request, 'usuarios/cadastro.html', {'form': form})


# ========================================================
# 2. NOVA VIEW DE PERFIL (GERENCIAMENTO E EXCLUSÃO)
# ========================================================
@login_required  # Se tentarem acessar sem login, o Django barra automaticamente
def perfil_usuario(request):
    user = request.user
    
    if request.method == 'POST':
        # Captura o clique no botão de atualizar os dados cadastrais
        if 'btn_atualizar' in request.POST:
            user.first_name = request.POST.get('first_name')
            user.last_name = request.POST.get('last_name')
            user.email = request.POST.get('email')
            user.save()
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('perfil')
            
        # Captura a confirmação do botão vermelho dentro do modal
        elif 'btn_deletar' in request.POST:
            user.delete()  # Remove o usuário do banco de dados permanentemente
            logout(request)  # Limpa a sessão ativa dele
            messages.success(request, 'Sua conta foi excluída permanentemente. Sentiremos sua falta!')
            return redirect('login')

    return render(request, 'usuarios/perfil.html')