# --- File: utils_openai.py --- #

# --- Libraries --- #
# Biblioteca para realizar requisições HTTP, usada para enviar dados à API da OpenAI.
import requests
import time
# Biblioteca para carregar variáveis de ambiente do arquivo .env.
from dotenv import load_dotenv, find_dotenv
import os  # Biblioteca para acessar variáveis de ambiente do sistema.

# --- Environment Setup --- #
# Carrega o arquivo .env que contém as credenciais sensíveis.
_ = load_dotenv(find_dotenv())


# --- Methods --- #
# API OPENAI ================================================

def retorna_resposta_modelo(mensagens: list, openai_key: str, modelo: str = 'gpt-4-turbo', temperatura: float = 0, stream: bool = False, max_retries: int = 5):
    """
    Envia uma solicitação para a API da OpenAI e retorna a resposta gerada pelo modelo.

    A função agora inclui um mecanismo de retry automático em caso de erro 429 (Too Many Requests), 
    implementando exponential backoff para evitar sobrecarga na API.

    Parâmetros:
    \n\t`mensagens (list)`: Lista de mensagens de entrada. Cada mensagem deve ser um dicionário com as chaves 'role' (identificando o remetente) e 'content' (conteúdo da mensagem).
    \n\t`openai_key (str)`: Chave da API da OpenAI usada para autenticação e autorização no serviço.
    \n\t`modelo (str)`: Nome do modelo a ser utilizado (padrão: 'gpt-4-turbo').
    \n\t`temperatura (float)`: Controla a aleatoriedade das respostas geradas. Valores altos (ex: 1.0) tornam as respostas mais criativas, enquanto valores baixos (ex: 0.2) tornam-nas mais focadas e determinísticas.
    \n\t`stream (bool)`: Se `True`, ativa o modo de transmissão contínua para obter resultados parciais em tempo real (padrão: `False`, retornando a resposta completa de uma vez).
    \n\t`max_retries (int)`: Número máximo de tentativas em caso de erro 429 (Too Many Requests). A cada tentativa, o tempo de espera dobra (Exponential Backoff). O padrão é `5`.

    Retorno:
    \n\t- Se `stream` for `True`, retorna um gerador que produz respostas parciais em tempo real.
    \n\t- Caso contrário, retorna a resposta completa do modelo como um JSON.
    \n\t- Se o erro 429 persistir após `max_retries`, uma exceção é lançada.

    Exemplo:
    >>> mensagens = [{"role": "user", "content": "Qual a capital da França?"}]
    >>> resposta = retorna_resposta_modelo(mensagens, "sua_api_key")
    >>> print(resposta)
    {"choices": [{"message": {"role": "assistant", "content": "A capital da França é Paris."}}]}
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

    wait_time = 2  # Começa com 2 segundos de espera
    retries = 0

    while retries < max_retries:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions", headers=headers, json=data, stream=stream
        )

        if response.status_code == 200:
            if stream:
                for line in response.iter_lines():
                    if line:
                        yield line.decode('utf-8')
            else:
                return response.json()

        elif response.status_code == 429:
            print(
                f"Erro 429: Muitas requisições. Tentativa {retries + 1}/{max_retries}. Aguardando {wait_time}s...")
            time.sleep(wait_time)
            wait_time *= 2  # Dobra o tempo de espera
            retries += 1

        else:
            response.raise_for_status()  # Levanta exceções para outros erros HTTP

    raise Exception(
        "Erro 429 persistente: Número máximo de tentativas atingido. Tente novamente mais tarde.")
