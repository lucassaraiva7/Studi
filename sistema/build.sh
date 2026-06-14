#!/usr/bin/env bash
# Interrompe o script se houver algum erro
set -o errexit

# Instala as dependências listadas no requirements.txt
pip install -r requirements.txt

# Junta todos os arquivos estáticos do sistema em uma única pasta
python manage.py collectstatic --no-input

# Aplica as tabelas no banco de dados do servidor
python manage.py migrate