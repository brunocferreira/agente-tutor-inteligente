# utils_openai.py
import requests

from dotenv import load_dotenv, find_dotenv
import os

# Carrega o arquivo .env
_ = load_dotenv(find_dotenv())

# API OPENAI ================================================


def retorna_resposta_modelo(mensagens, openai_key, modelo='gpt-3.5-turbo', temperatura=0, stream=False):
    """
    Função para retornar a mensagem do modelo.

    Parâmetros:
    - `mensagens` (list): Uma lista de mensagens de entrada para o modelo. Cada mensagem deve ser um dicionário com as chaves 'role' (basicamente o usuário) e 'content' (a mensagem em si).
    - `openai_key` (str): Chave da API da OpenAI usada para autenticação e autorização no serviço da OpenAI.
    - `modelo` (str): O nome do modelo a ser usado (padrão é 'gpt-3.5-turbo').
    - `temperatura` (float): Controla a aleatoriedade das respostas geradas. Valores mais altos como 1.0 tornam as saídas mais criativas, enquanto valores mais baixos como 0.2 as tornam mais focadas e determinísticas.
    - `stream` (bool): Se `True`, ativa o modo de transmissão contínua para obter resultados parciais em tempo real (padrão é `False`, que obtém o resultado apenas após a mensagem estar completa).

    Retorna:
    - Uma mensagem gerada pelo modelo com base nas mensagens de entrada e parâmetros fornecidos.
    """
    headers = {
        "Authorization": f"Bearer {openai_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": modelo,
        "messages": mensagens,
        "temperature": temperatura,
        "stream": stream
    }

    response = requests.post(
        "https://api.openai.com/v1/chat/completions", headers=headers, json=data, stream=stream)

    if response.status_code == 200:
        if stream:
            for line in response.iter_lines():
                if line:
                    yield line.decode('utf-8')
        else:
            return response.json()
    else:
        response.raise_for_status()
