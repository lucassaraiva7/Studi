# Usa a imagem oficial do Python (mesma versão 3.13 que você usa)
FROM python:3.13-slim

# Evita que o Python grave arquivos .pyc no contêiner
ENV PYTHONDONTWRITEBYTECODE=1
# Garante que os logs do terminal sejam exibidos em tempo real
ENV PYTHONUNBUFFERED=1

# Define a pasta de trabalho dentro do contêiner
WORKDIR /app

# Copia o arquivo de dependências e instala as bibliotecas
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o restante do código do projeto para dentro do contêiner
COPY . /app/

# Expõe a porta padrão do Django
EXPOSE 8000

# Comando padrão para rodar o servidor do Django apontando para qualquer IP externo
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]