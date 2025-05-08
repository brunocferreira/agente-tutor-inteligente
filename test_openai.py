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


def get_api_key(provided_api_key: str = None) -> str:
    """
    Retorna a chave da API a partir do parâmetro informado ou das variáveis de ambiente.
    Caso a chave não seja encontrada, lança um erro solicitando sua inserção.

    Parâmetros:
        provided_api_key (str): Chave da API informada na chamada da função.

    Retorno:
        str: Chave da API.
    """
    key = provided_api_key if provided_api_key else os.getenv("OPENAI_API_KEY")
    if not key:
        raise ValueError(
            "A chave da API não foi encontrada. Insira a chave na variável .env ou passe para a função test.")
    return key


# --- Methods --- #
def mask_api_key(api_key: str = None) -> str:
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
    if (api_key == None):
        return print("Erro: API_KEY não definida. Insira a sua chave da API da OpenAI para o teste ou a defina em .env")
    if len(api_key) < 10:
        raise ValueError("A chave deve ter pelo menos 10 caracteres.")
    return f"{api_key[:5]}*****{api_key[-5:]}"


def test(api_key: str = None, model: str = 'gpt-3.5-turbo', temperature: float = 0, stream: bool = False) -> None:
    """
    Testa a conexão com a API da OpenAI enviando uma mensagem de verificação.

    Parâmetros:
    \n\t`api_key (str)`: Chave da API a ser utilizada. Se não for passada, a função utiliza a variável de ambiente.
    \n\t`model (str)`: Nome do modelo a ser utilizado (padrão: 'gpt-3.5-turbo').
    \n\t`temperature (float)`: Grau de aleatoriedade na resposta do modelo (padrão: 0).
    \n\t`stream (bool)`: Define se a resposta será transmitida em partes (padrão: False).

    Retorno:
    \n\t`None`: A função imprime a resposta do modelo no console.

    Exemplo:
    >>> test(api_key, model='gpt-3.5-turbo', temperature=0.7, stream=False)
    "Sim, estou aqui! Como posso ajudar?"
    """
    # Obtém e valida a chave da API
    chave = get_api_key(api_key)
    print("Chave API mascarada:", mask_api_key(chave))

    # Instancia o cliente utilizando a chave
    client = openai.OpenAI(api_key=chave)

    try:
        # Criação do cliente com a API Key
        response = client.chat.completions.create(
            # response = openai.ChatCompletion.create(
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

        if stream:
            for chunk in response:
                # Alguns chunks podem não conter o campo 'content'
                content = chunk.choices[0].delta.get("content", "")
                print(content, end="", flush=True)
        else:
            print(response.choices[0].message.content)

    except Exception as e:
        print("Erro ao acessar client.chat.completions.create:", e)
        print("Certifique-se de que a versão da OpenAI esteja na 1.59.9.")


# Executa o teste
if __name__ == '__main__':
    # Chamada de teste; se desejar, passe a chave como parâmetro ou deixe que ela seja carregada do .env
    test()
