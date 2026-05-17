import os
import json
import pypdf
import google.generativeai as genai
from django.conf import settings

# Configura a chave de API que vamos colocar no seu settings.py logo mais
genai.configure(api_key=getattr(settings, "GEMINI_API_KEY", "SUA_CHAVE_AQUI"))

def extrair_texto_pdf(arquivo_fisico):
    """
    Recebe o arquivo PDF vindo do formulário,
    extrai o texto de todas as páginas e junta tudo em uma string.
    """
    texto_completo = ""
    try:
        reader = pypdf.PdfReader(arquivo_fisico)
        for page in reader.pages:
            texto_da_pagina = page.extract_text()
            if texto_da_pagina:
                texto_completo += texto_da_pagina + "\n"
    except Exception as e:
        raise ValueError(f"Erro ao ler o arquivo PDF: {str(e)}")
    
    return texto_completo


def gerar_flashcards_com_ia(texto_do_pdf):
    """
    Envia o texto do PDF para o Gemini e exige
    um retorno estritamente formatado em JSON com perguntas e respostas.
    """
    # Usamos o modelo flash para processamento rápido de textos
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""
    Você é um especialista em educação e memorização espaçada.
    Com base no texto fornecido abaixo, extraído de um material de estudos, crie uma lista de flashcards (perguntas e respostas diretas).
    
    Diretrizes fundamentais:
    1. Foque nos conceitos mais importantes, fórmulas, definições ou fatos históricos.
    2. As perguntas devem ser claras e objetivas.
    3. As respostas devem ser curtas e diretas ao ponto (ideais para memorização ativa).

    Você DEVE retornar a resposta estritamente no formato JSON, respeitando a seguinte estrutura de chaves:
    [
      {{"question": "Sua pergunta aqui?", "answer": "Sua resposta curta aqui"}},
      {{"question": "Outra pergunta?", "answer": "Outra resposta"}}
    ]

    Texto do documento:
    {texto_do_pdf}
    """

    try:
        # Travamos a API para que ela responda apenas em formato JSON estruturado
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        
        # Converte a string JSON recebida em uma lista Python comum
        flashcards_list = json.loads(response.text)
        return flashcards_list

    except json.JSONDecodeError:
        raise ValueError("A inteligência artificial não retornou um JSON válido. Tente novamente.")
    except Exception as e:
        raise RuntimeError(f"Erro na comunicação com a API de IA: {str(e)}")