import os
import openai
from dotenv import load_dotenv, find_dotenv
# Carrega o arquivo .env
_ = load_dotenv(find_dotenv())

# Obtém a chave da API
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("A chave da API não foi encontrada no arquivo .env")


def mask_api_key(api_key):
    """
    Retorna a chave da API mascarada, exibindo os 5 primeiros e os 5 últimos caracteres,
    com 5 asteriscos no meio.

    Parâmetros:
    - api_key (str): A chave completa da API.

    Retorna:
    - str: A chave mascarada.
    """
    if len(api_key) < 10:
        raise ValueError("A chave deve ter pelo menos 10 caracteres.")
    return f"{api_key[:5]}*****{api_key[-5:]}"


# Exibe a chave mascarada
mascarada = mask_api_key(api_key)
print(mascarada)


def test(api_key, model='gpt-3.5-turbo', temperature=0, stream=False):
    """
    Função principal para executar uma chamada assíncrona ao modelo GPT-3.5-turbo.

    Parâmetros:
    - `api_key` (str): Chave da API da OpenAI.
    - `model` (str): O nome do modelo a ser usado (padrão é 'gpt-3.5-turbo').
    - `temperature` (float): Controla a aleatoriedade das respostas geradas.
    - `stream` (bool): Se True, ativa o modo de transmissão contínua para obter resultados parciais em tempo real.
    """
    # Faz a solicitação
    try:
        openai.api_key = api_key
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": "Teste de conexão. Tem alguém aí? Se sim, me responda com poucas palavras.",
                },
            ],
            temperature=temperature,
            stream=stream,
        )
        print(response['choices'][0]['message']['content'])
    except Exception as e:
        print("Erro ao acessar ChatCompletion.create:", e)
        print("Certifique que a versão da openai é a 0.28")


# Executa o código test
test(api_key)
