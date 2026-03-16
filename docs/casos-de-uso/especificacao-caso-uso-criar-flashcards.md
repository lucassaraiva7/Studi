# Caso de Uso – Cadastrar Matéria

## Informações Gerais

| Campo | Descrição |
|------|-----------|
| Nome do Caso de Uso | Cadastrar Matéria |
| Ator | Usuário |
| Descrição | Permite que o usuário cadastre uma nova matéria para organizar seus conteúdos de estudo e flashcards. |
| Pré-condição | O usuário deve estar autenticado no sistema. |
| Pós-condição | A matéria é registrada no sistema e fica disponível para organização dos conteúdos. |

---

## Fluxo Principal

| Passo | Ação |
|------|------|
| 1 | O usuário acessa a opção **Cadastrar Matéria** no sistema |
| 2 | O sistema apresenta o formulário de cadastro |
| 3 | O usuário informa o nome da matéria |
| 4 | O usuário pode informar uma descrição opcional |
| 5 | O usuário confirma o cadastro |
| 6 | O sistema valida os dados informados |
| 7 | O sistema salva a matéria no banco de dados |
| 8 | O sistema confirma o cadastro ao usuário |

---

## Fluxos de Exceção

| Código | Descrição |
|------|-----------|
| EX01 | Caso o campo nome da matéria não seja preenchido, o sistema solicita o preenchimento |
| EX02 | Caso ocorra erro no armazenamento dos dados, o sistema informa que não foi possível cadastrar |

---

## Dicionário de Dados – Matéria

| Nome Campo | Descrição | Obrigatoriedade | Tipo | Tamanho | Máscara | Default | RegExp |
|------------|-----------|----------------|------|---------|---------|---------|--------|
| id_materia | Identificador único da matéria | Sim | Inteiro | 10 | N/A | Auto | N/A |
| nome_materia | Nome da matéria cadastrada | Sim | Texto | 100 | N/A | N/A | N/A |
| descricao | Descrição da matéria | Não | Texto | 255 | N/A | N/A | N/A |
| data_criacao | Data de criação da matéria | Sim | Data | N/A | DD/MM/AAAA | Data atual | N/A |
