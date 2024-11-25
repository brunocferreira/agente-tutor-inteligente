# utils_openai.py
import openai

# API OPENAI ================================================


def retorna_resposta_modelo(mensagens,
                            openai_key,
                            modelo='gpt-3.5-turbo',
                            temperatura=0,
                            stream=False):
    """
    Função para retornar a mensagem do modelo.

    Parâmetros:
    - `mensagens` (list): Uma lista de mensagens de entrada para o modelo. Cada mensagem deve ser um dicionário com as chaves 'role' (basicamente o usuário) e 'content' (a mensagem em sí).
    - `openai_key` (str): Chave da API da OpenAI usada para autenticação e autorização no serviço da OpenAI.
    - `modelo` (str): O nome do modelo a ser usado (padrão é 'gpt-3.5-turbo').
    - `temperatura` (float): Controla a aleatoriedade das respostas geradas. Valores mais altos como 1.0 tornam as saídas mais criativas, enquanto valores mais baixos como 0.2 as tornam mais focadas e determinísticas.
    - `stream` (bool): Se `True`, ativa o modo de transmissão contínua para obter resultados parciais em tempo real (padrão é `False` que obtem o resultado apenas após a mensagem estar completa).

    Retorna:
    - Uma mensagem gerada pelo modelo com base nas mensagens de entrada e parâmetros fornecidos.
    """
    openai.api_key = openai_key
    response = openai.ChatCompletion.create(
        model=modelo,
        messages=mensagens,
        temperature=temperatura,
        stream=stream
    )
    return response
