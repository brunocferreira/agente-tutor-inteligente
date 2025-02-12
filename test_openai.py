# --- File: test_openai.py --- #

# --- Libraries --- #
# Biblioteca padrão para manipulação de variáveis de ambiente e sistema operacional.
import os
# Biblioteca da OpenAI para acesso à API de modelos de linguagem.
import openai
# Biblioteca para carregar variáveis de ambiente de um arquivo .env.
from dotenv import load_dotenv, find_dotenv

# --- Environment Setup --- #
# Carrega o arquivo .env que contém as credenciais sensíveis
_ = load_dotenv(find_dotenv())

# Obtém a chave da API da OpenAI a partir do arquivo .env
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("A chave da API não foi encontrada no arquivo .env")


# --- Methods --- #
def mask_api_key(api_key: str) -> str:
    """
    Mascara a chave da API para exibição segura.

    Parâmetros:
    \n\t`api_key (str)`: A chave de API completa.

    Retorno:
    \n\t`str`: A chave mascarada com os cinco primeiros e últimos caracteres visíveis.

    Exemplo:
    >>> mask_api_key("sk-12345ABCDE67890FGHIJ")
    'sk-12345*****FGHIJ'
    """
    if len(api_key) < 10:
        raise ValueError("A chave deve ter pelo menos 10 caracteres.")
    return f"{api_key[:5]}*****{api_key[-5:]}"


# Exibe a chave mascarada
mascarada = mask_api_key(api_key)
print(mascarada)


def test(api_key: str, model: str = 'gpt-3.5-turbo', temperature: float = 0, stream: bool = False) -> None:
    """
    Testa a conexão com a API da OpenAI enviando uma mensagem de verificação.

    Parâmetros:
    \n\t`api_key (str)`: Chave da API OpenAI.
    \n\t`model (str)`: Nome do modelo a ser utilizado (padrão: 'gpt-3.5-turbo').
    \n\t`temperature (float)`: Grau de aleatoriedade na resposta do modelo (padrão: 0).
    \n\t`stream (bool)`: Define se a resposta será transmitida em partes (padrão: False).

    Retorno:
    \n\t`None`: A função imprime a resposta do modelo no console.

    Exemplo:
    >>> test(api_key, model='gpt-3.5-turbo', temperature=0.7, stream=False)
    "Sim, estou aqui! Como posso ajudar?"
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
        print("Certifique que a versão da openai é a 1.59.9")


# Executa o código test
test(api_key)
