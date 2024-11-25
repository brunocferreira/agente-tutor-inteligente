# utils_file.py
from unidecode import unidecode
import re
from pathlib import Path
import pickle

import os
from dotenv import load_dotenv, find_dotenv
# Carrega o arquivo .env
_ = load_dotenv(find_dotenv())

# Obtém a chave da API
api_key = os.getenv("OPENAI_API_KEY")


PASTA_CONFIGERACOES = Path(__file__).parent / 'configuracoes'
PASTA_CONFIGERACOES.mkdir(exist_ok=True)
PASTA_MENSAGENS = Path(__file__).parent / 'mensagens'
PASTA_MENSAGENS.mkdir(exist_ok=True)
CACHE_DESCONVERTE = {}


# SALVAMENTO E LEITURA DE CONVERSAS ========================

def converte_nome_mensagem(nome_mensagem):
    """
    Função para converter o nome da mensagem em um formato adequado para ser usado como nome de arquivo.

    Parâmetros:
    - `nome_mensagem` (str): O nome da mensagem a ser convertido.

    Retorna:
    - `nome_arquivo` (str): O nome da mensagem convertido, sem acentuações e caracteres especiais, em minúsculas.
    """
    nome_arquivo = unidecode(nome_mensagem)
    nome_arquivo = re.sub(r'\W+', '', nome_arquivo).lower()
    return nome_arquivo


def desconverte_nome_mensagem(nome_arquivo):
    """
    Função para obter o nome da mensagem original a partir do nome do arquivo.

    Parâmetros:
    - `nome_arquivo` (str): O nome do arquivo.

    Retorna:
    - `nome_mensagem` (str): O nome da mensagem original associada ao nome do arquivo.
    """
    if not nome_arquivo in CACHE_DESCONVERTE:
        nome_mensagem = ler_mensagem_por_nome_arquivo(
            nome_arquivo, key='nome_mensagem')
        CACHE_DESCONVERTE[nome_arquivo] = nome_mensagem
    return CACHE_DESCONVERTE[nome_arquivo]


def retorna_nome_da_mensagem(mensagens):
    """
    Função para retornar o nome da mensagem a partir de uma lista de mensagens.

    Parâmetros:
    - `mensagens` (list): Uma lista de mensagens. Cada mensagem deve ser um dicionário com as chaves 'role' e 'content'.

    Retorna:
    - `nome_mensagem` (str): O conteúdo da primeira mensagem do usuário, limitado aos primeiros 30 caracteres.
    """
    nome_mensagem = ''
    for mensagem in mensagens:
        if mensagem['role'] == 'user':
            nome_mensagem = mensagem['content'][:30]
            break
    return nome_mensagem


def salvar_mensagens(mensagens):
    """
    Função para salvar uma lista de mensagens em um arquivo.

    Parâmetros:
    - `mensagens` (list): Uma lista de mensagens a serem salvas.

    Retorna:
    - `bool`: Retorna `False` se a lista de mensagens estiver vazia, caso contrário, salva as mensagens em um arquivo.

    A função salva as mensagens em um arquivo cujo nome é derivado do conteúdo da mensagem do usuário.
    """
    if len(mensagens) == 0:
        return False
    nome_mensagem = retorna_nome_da_mensagem(mensagens)
    nome_arquivo = converte_nome_mensagem(nome_mensagem)
    arquivo_salvar = {
        'nome_mensagem': nome_mensagem,
        'nome_arquivo': nome_arquivo,
        'mensagem': mensagens
    }
    with open(PASTA_MENSAGENS / nome_arquivo, 'wb') as f:
        pickle.dump(arquivo_salvar, f)


def ler_mensagem_por_nome_arquivo(nome_arquivo, key='mensagem'):
    """
    Função para ler uma mensagem específica a partir do nome do arquivo.

    Parâmetros:
    - `nome_arquivo` (str): O nome do arquivo que contém a mensagem.
    - `key` (str): A chave específica para acessar no dicionário de mensagens (padrão é 'mensagem').

    Retorna:
    - A mensagem correspondente à chave fornecida, lida do arquivo.
    """
    with open(PASTA_MENSAGENS / nome_arquivo, 'rb') as f:
        mensagens = pickle.load(f)
    return mensagens[key]


def ler_mensagens(mensagens, key='mensagem'):
    """
    Função para ler mensagens a partir de uma lista de mensagens fornecida.

    Parâmetros:
    - `mensagens` (list): Uma lista de mensagens. Cada mensagem deve ser um dicionário com as chaves 'role' e 'content'.
    - `key` (str): A chave específica para acessar no dicionário de mensagens (padrão é 'mensagem').

    Retorna:
    - `list`: Uma lista de mensagens correspondente à chave fornecida, lida do arquivo, ou uma lista vazia se nenhuma mensagem for fornecida.
    """
    if len(mensagens) == 0:
        return []
    nome_mensagem = retorna_nome_da_mensagem(mensagens)
    nome_arquivo = converte_nome_mensagem(nome_mensagem)
    with open(PASTA_MENSAGENS / nome_arquivo, 'rb') as f:
        mensagens = pickle.load(f)
    return mensagens[key]


def listar_conversas():
    """
    Função para listar todas as conversas salvas, ordenadas pelo tempo de modificação.

    Retorna:
    - `list`: Uma lista de nomes de conversas (sem a extensão do arquivo), ordenadas pela última modificação, da mais recente para a mais antiga.
    """
    conversas = list(PASTA_MENSAGENS.glob('*'))
    conversas = sorted(
        conversas, key=lambda item: item.stat().st_mtime_ns, reverse=True)
    return [c.stem for c in conversas]


# SALVAMENTO E LEITURA DA APIKEY ========================


def salva_chave(chave):
    """
    Função para salvar uma chave de configuração em um arquivo.

    Parâmetros:
    - `chave` (str): A chave de configuração a ser salva.

    A chave é salva no diretório `PASTA_CONFIGURACOES` com o nome de arquivo 'chave'.
    """
    with open(PASTA_CONFIGERACOES / 'chave', 'wb') as f:
        pickle.dump(chave, f)


def le_chave():
    """
    Função para ler uma chave de configuração a partir de um arquivo ou do arquivo .env.

    Retorna:
    - `str`: A chave de configuração lida do arquivo, ou uma string vazia se o arquivo não existir.

    A função verifica se o arquivo 'chave' existe no diretório `PASTA_CONFIGERACOES` antes de tentar ler a chave.
    Se o arquivo não existir, tenta ler a chave do arquivo .env.
    """
    if (PASTA_CONFIGERACOES / 'chave').exists():
        with open(PASTA_CONFIGERACOES / 'chave', 'rb') as f:
            return pickle.load(f)
    else:
        # Obtém a chave da API do arquivo .env
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            return api_key
        else:
            return ''
