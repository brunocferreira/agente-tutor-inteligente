# main.py
import os

import openai
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

api_key = os.getenv('OPENAI_API_KEY')
print(api_key)  # use apenas para teste


def return_model_res(messages, openai_api_key, model='gpt-3.5-turbo', temperature=0, stream=False):
    """
    Função para retornar a mensagem do modelo.

    Parâmetros:
    - `messages` (list): Uma lista de mensagens de entrada para o modelo. Cada mensagem deve ser um dicionário com as chaves 'role' (basicamente o usuário) e 'content' (a mensagem em sí).
    - `openai_api_key` (str): Chave da API da OpenAI usada para autenticação e autorização no serviço da OpenAI.
    - `model` (str): O nome do modelo a ser usado (padrão é 'gpt-3.5-turbo').
    - `temperature` (float): Controla a aleatoriedade das respostas geradas. Valores mais altos como 1.0 tornam as saídas mais criativas, enquanto valores mais baixos como 0.2 as tornam mais focadas e determinísticas.
    - `stream` (bool): Se `True`, ativa o modo de transmissão contínua para obter resultados parciais em tempo real (padrão é `False` que obtem o resultado apenas após a mensagem estar completa).

    Retorna:
    - Uma mensagem gerada pelo modelo com base nas mensagens de entrada e parâmetros fornecidos.
    """
    # Define a chave da API
    openai.api_key = openai_api_key

    # Criação da solicitação para o modelo
    if not stream:
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=temperature
        )
        return response['choices'][0]['message']['content']
    else:
        # Modo de transmissão contínua
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=temperature,
            stream=True
        )
        # Gerar o conteúdo gradualmente
        collected_chunks = []
        for chunk in response:
            if 'choices' in chunk:
                delta = chunk['choices'][0]['delta']
                if 'content' in delta:
                    collected_chunks.append(delta['content'])
        return ''.join(collected_chunks)


mensagens = [{'role': 'user', 'content': 'Defina uma maçã em 5 palavras'}]
resposta = return_model_res(mensagens, api_key)
print(resposta)
