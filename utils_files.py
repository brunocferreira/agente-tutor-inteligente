# --- File: utils_file.py --- #

# --- Libraries --- #
import streamlit as st  # Framework para criar interfaces web interativas.
import os  # Biblioteca para manipulação de arquivos e variáveis de ambiente.
import re  # Biblioteca para expressões regulares.
# Biblioteca para serialização e desserialização de objetos Python.
import pickle
import json  # Biblioteca para manipulação de arquivos JSON.
import requests  # Biblioteca para fazer requisições HTTP.
import pydub  # Biblioteca para manipulação de arquivos de áudio.

# Remove acentos e caracteres especiais de strings.
from unidecode import unidecode
from pathlib import Path  # Manipulação de caminhos de arquivos e diretórios.

# Bibliotecas do LangChain para processamento de linguagem natural e recuperação de documentos.
# Implementação de um fluxo de recuperação conversacional de informações.
from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
# Armazena o histórico da conversa para ser reutilizado durante a interação.
from langchain.memory import ConversationBufferMemory
# Permite a criação de templates para estruturar prompts usados nos modelos de IA.
from langchain.prompts import PromptTemplate
# Carrega e processa documentos PDF para serem utilizados na recuperação de informações.
from langchain_community.document_loaders.pdf import PyPDFLoader
# Utiliza a biblioteca FAISS para armazenar e recuperar embeddings de documentos.
from langchain_community.vectorstores.faiss import FAISS
# Divide textos longos em segmentos menores de maneira recursiva para otimizar a recuperação de informações.
from langchain_text_splitters import RecursiveCharacterTextSplitter
# Gera embeddings de texto usando modelos da OpenAI.
from langchain_openai.embeddings import OpenAIEmbeddings
# Implementa um modelo de chat baseado na OpenAI para geração de respostas contextuais.
from langchain_openai.chat_models import ChatOpenAI

# Biblioteca para carregar variáveis de ambiente do arquivo .env.
from dotenv import load_dotenv, find_dotenv
from configs import *  # Importa configurações do sistema.
from assets import *  # Importa estilos e scripts auxiliares.
from moviepy import *  # Biblioteca para manipulação de vídeos.
# Importa funções auxiliares para integração com OpenAI.
from utils_openai import *
from io import BytesIO  # Biblioteca para manipulação de fluxos de bytes.

# --- Environment Setup --- #
# Carrega o arquivo .env que contém as credenciais sensíveis.
_ = load_dotenv(find_dotenv())

# Obtém a chave da API da OpenAI.
api_key = os.getenv("OPENAI_API_KEY")


# --- Directory Setup --- #
PASTA_CONFIGERACOES = Path(__file__).parent / 'configuracoes'
PASTA_CONFIGERACOES.mkdir(exist_ok=True)
PASTA_MENSAGENS = Path(__file__).parent / 'mensagens'
PASTA_MENSAGENS.mkdir(exist_ok=True)
PASTA_ARQUIVOS = Path(__file__).parent / 'arquivos'
PASTA_ARQUIVOS.mkdir(exist_ok=True)
PASTA_TEMP = Path(__file__).parent / 'temp'
PASTA_TEMP.mkdir(exist_ok=True)

# Arquivos temporários
ARQUIVO_AUDIO_TEMP = PASTA_TEMP / 'audio.mp3'
ARQUIVO_MIC_TEMP = PASTA_TEMP / 'mic.mp3'
ARQUIVO_VIDEO_TEMP = PASTA_TEMP / 'video.mp4'
ARQUIVO_FOTO_TEMP = PASTA_TEMP / 'foto.jpeg'

# Cache para otimizar conversões
CACHE_DESCONVERTE = {}


# --- Methods --- #
# SALVAMENTO E LEITURA DE CONVERSAS ========================

def converte_nome_mensagem(nome_mensagem: str) -> str:
    """
    Converte o nome da mensagem para um formato adequado para uso como nome de arquivo.

    Parâmetros:
    \n\t`nome_mensagem (str)`: O nome da mensagem a ser convertido.

    Retorno:
    \n\t`str`: Nome da mensagem convertido, sem acentos e caracteres especiais, em minúsculas.
    """
    nome_arquivo = unidecode(nome_mensagem)
    nome_arquivo = re.sub(r'\W+', '', nome_arquivo).lower()
    return nome_arquivo


def desconverte_nome_mensagem(nome_arquivo: str) -> str:
    """
    Obtém o nome original da mensagem a partir do nome do arquivo.

    Parâmetros:
    \n\t`nome_arquivo (str)`: O nome do arquivo.

    Retorno:
    \n\t`str`: Nome original associado ao arquivo.
    """
    if not nome_arquivo in CACHE_DESCONVERTE:
        nome_mensagem = ler_mensagem_por_nome_arquivo(
            nome_arquivo, key='nome_mensagem')
        CACHE_DESCONVERTE[nome_arquivo] = nome_mensagem
    return CACHE_DESCONVERTE[nome_arquivo]


def retorna_nome_da_mensagem(mensagens: list) -> str:
    """
    Retorna o nome da mensagem com base na primeira mensagem enviada pelo usuário.

    Parâmetros:
    \n\t`mensagens (list)`: Lista de mensagens contendo dicionários com chaves 'role' e 'content'.

    Retorno:
    \n\t`str`: Conteúdo da primeira mensagem do usuário, limitado aos primeiros 30 caracteres.

    Exemplo:
    >>> mensagens = [{"role": "user", "content": "Este é um exemplo de mensagem longa."}]
    >>> retorna_nome_da_mensagem(mensagens)
    "Este é um exemplo de mensagem longa."
    """
    nome_mensagem = ''
    for mensagem in mensagens:
        if mensagem['role'] == 'user':
            nome_mensagem = mensagem['content'][:30]
            break
    return nome_mensagem


def salvar_mensagens(mensagens: list) -> bool:
    """
    Salva uma lista de mensagens em um arquivo utilizando `pickle`.

    Parâmetros:
    \n\t`mensagens (list)`: Lista de mensagens contendo dicionários com chaves 'role' e 'content'.

    Retorno:
    \n\t`bool`: Retorna `False` se a lista de mensagens estiver vazia; caso contrário, salva e retorna `True`.

    Exemplo:
    >>> mensagens = [{"role": "user", "content": "Olá!"}]
    >>> salvar_mensagens(mensagens)
    True
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
    return True


def ler_mensagem_por_nome_arquivo(nome_arquivo: str, key: str = 'mensagem'):
    """
    Lê uma mensagem salva a partir do nome do arquivo.

    Parâmetros:
    \n\t`nome_arquivo (str)`: Nome do arquivo contendo a mensagem salva.
    \n\t`key (str)`: Chave específica dentro do dicionário salvo para ser retornada (padrão: 'mensagem').

    Retorno:
    \n\t`dict | str`: Conteúdo correspondente à chave especificada dentro do arquivo salvo.

    Exemplo:
    >>> ler_mensagem_por_nome_arquivo('exemplo_mensagem')
    [{"role": "user", "content": "Olá!"}]
    """
    with open(PASTA_MENSAGENS / nome_arquivo, 'rb') as f:
        mensagens = pickle.load(f)
    return mensagens[key]


def ler_mensagens(mensagens: list, key: str = 'mensagem') -> list:
    """
    Lê mensagens a partir de uma lista fornecida, recuperando os dados armazenados em arquivos.

    Parâmetros:
    \n\t`mensagens (list)`: Lista contendo mensagens em formato de dicionário com as chaves 'role' e 'content'.
    \n\t`key (str)`: Chave do dicionário armazenado para retornar a informação desejada (padrão: 'mensagem').

    Retorno:
    \n\t`list`: Lista de mensagens lidas do arquivo correspondente ou uma lista vazia se nenhum dado for encontrado.

    Exemplo:
    >>> mensagens = [{"role": "user", "content": "Olá!"}]
    >>> ler_mensagens(mensagens)
    [{"role": "user", "content": "Olá!"}]
    """
    if len(mensagens) == 0:
        return []
    nome_mensagem = retorna_nome_da_mensagem(mensagens)
    nome_arquivo = converte_nome_mensagem(nome_mensagem)
    with open(PASTA_MENSAGENS / nome_arquivo, 'rb') as f:
        mensagens = pickle.load(f)
    return mensagens[key]


def listar_conversas() -> list:
    """
    Lista todas as conversas salvas, ordenadas pela última modificação.

    Retorno:
    \n\t`list`: Lista dos nomes das conversas armazenadas, ordenadas da mais recente para a mais antiga.

    Exemplo:
    >>> listar_conversas()
    ['conversa1', 'conversa2']
    """
    conversas = list(PASTA_MENSAGENS.glob('*'))
    conversas = sorted(
        conversas, key=lambda item: item.stat().st_mtime_ns, reverse=True)
    return [c.stem for c in conversas]


# SALVAMENTO E LEITURA DA APIKEY ========================

def salva_chave(chave: str) -> None:
    """
    Salva a chave da API da OpenAI em um arquivo utilizando serialização com `pickle`.

    Parâmetros:
    \n\t`chave (str)`: Chave da API a ser salva.

    Exemplo:
    >>> salva_chave("sk-12345ABCDE67890FGHIJ")
    """
    with open(PASTA_CONFIGERACOES / 'chave', 'wb') as f:
        pickle.dump(chave, f)


def le_chave() -> str:
    """
    Lê a chave da API salva em um arquivo ou do arquivo .env.

    Retorno:
    \n\t`str`: Chave lida do arquivo ou do ambiente. Retorna uma string vazia se não for encontrada.

    Exemplo:
    >>> le_chave()
    'sk-12345ABCDE67890FGHIJ'
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


# RAG com LANGCHAIN ========================

def importacao_documentos() -> list:
    """
    Carrega documentos PDF da pasta de arquivos e os transforma em uma lista de documentos processáveis.

    Retorno:
    \n\t`list`: Lista de documentos carregados a partir dos arquivos PDF disponíveis.

    Exemplo:
    >>> documentos = importacao_documentos()
    >>> print(len(documentos))
    5
    """
    documentos = []
    for arquivo in PASTA_ARQUIVOS.glob('*.pdf'):
        loader = PyPDFLoader(str(arquivo))
        documentos_arquivo = loader.load()
        documentos.extend(documentos_arquivo)
    return documentos


def split_de_documentos(documentos: list) -> list:
    """
    Divide documentos longos em trechos menores para facilitar a recuperação de informações.

    Parâmetros:
    \n\t`documentos (list)`: Lista de documentos a serem fragmentados.

    Retorno:
    \n\t`list`: Lista de documentos segmentados, prontos para processamento.

    Exemplo:
    >>> documentos = split_de_documentos(importacao_documentos())
    >>> print(len(documentos))
    20
    """
    recur_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2500,
        chunk_overlap=250,
        separators=["/n\n", "\n", ".", " ", ""]
    )
    documentos = recur_splitter.split_documents(documentos)

    for i, doc in enumerate(documentos):
        doc.metadata['source'] = doc.metadata['source'].split('/')[-1]
        doc.metadata['doc_id'] = i
    return documentos


def cria_vector_store(documentos: list):
    """
    Cria um armazenamento vetorial utilizando FAISS a partir de uma lista de documentos segmentados.

    Parâmetros:
    \n\t`documentos (list)`: Lista de documentos processados e divididos em trechos menores.

    Retorno:
    \n\t`FAISS`: Um índice FAISS contendo os embeddings dos documentos para recuperação eficiente de informações.

    Exemplo:
    >>> documentos = split_de_documentos(importacao_documentos())
    >>> vector_store = cria_vector_store(documentos)
    >>> print(vector_store)
    <langchain_community.vectorstores.faiss.FAISS object at 0x...>
    """
    try:
        embedding_model = OpenAIEmbeddings()
        print("Embedding model initialized successfully.")
        vector_store = FAISS.from_documents(
            documents=documentos,
            embedding=embedding_model
        )
        return vector_store
    except Exception as e:
        print("Failed to initialize embedding model:", e)


def cria_chain_conversa():
    """
    Cria a cadeia de conversação utilizando LangChain para recuperação de informações baseada em conversas anteriores e documentos fornecidos.

    Retorno:
    \n\t`None`: A função não retorna nada explicitamente, mas armazena a cadeia no estado da sessão do Streamlit.

    Exemplo:
    >>> cria_chain_conversa()
    >>> print(st.session_state['chain'])
    <langchain.chains.conversational_retrieval.base.ConversationalRetrievalChain object at 0x...>
    """

    documentos = importacao_documentos()
    documentos = split_de_documentos(documentos)
    vector_store = cria_vector_store(documentos)

    chat = ChatOpenAI(model=get_config('modelo'))
    memory = ConversationBufferMemory(
        return_messages=True,
        memory_key='chat_history',
        output_key='answer'
    )
    retriever = vector_store.as_retriever(
        search_type=get_config('retrieval_search_type'),
        search_kwargs=get_config('retrieval_kwargs')
    )
    prompt = PromptTemplate.from_template(get_config('prompt'))
    chat_chain = ConversationalRetrievalChain.from_llm(
        llm=chat,
        memory=memory,
        retriever=retriever,
        return_source_documents=True,
        verbose=True,
        combine_docs_chain_kwargs={'prompt': prompt}
    )

    st.session_state['chain'] = chat_chain


# FUNÇÕES ==================================================


def seleciona_conversa(nome_arquivo: str) -> None:
    """
    Seleciona uma conversa existente ou cria uma nova sessão de conversa.

    Parâmetros:
    \n\t`nome_arquivo (str)`: Nome do arquivo da conversa a ser carregada. Se for uma string vazia, inicia uma nova conversa.

    Retorno:
    \n\t`None`: Atualiza o estado da sessão do Streamlit com a conversa selecionada.

    Exemplo:
    >>> seleciona_conversa('conversa1')
    >>> print(st.session_state['conversa_atual'])
    'conversa1'
    """
    if nome_arquivo == '':
        st.session_state['mensagens'] = []
    else:
        mensagem = ler_mensagem_por_nome_arquivo(nome_arquivo)
        st.session_state['mensagens'] = mensagem
    st.session_state['conversa_atual'] = nome_arquivo


def mascarar_chave(chave: str) -> str:
    """
    Mascarar uma chave API para exibição segura, ocultando parte dos caracteres.

    Parâmetros:
    \n\t`chave (str)`: A chave API a ser mascarada.

    Retorno:
    \n\t`str`: Chave mascarada com os primeiros 5 e os últimos 5 caracteres visíveis.

    Exemplo:
    >>> mascarar_chave("sk-12345ABCDE67890FGHIJ")
    'sk-12345***FGHIJ'
    """
    if len(chave) > 10:
        return chave[:5] + '***' + chave[-5:]
    else:
        return chave


def nova_mensagem(prompt: str, mensagens: list, flag: bool = False, placeholder=None) -> None:
    """
    Adiciona uma nova mensagem ao histórico de conversas e exibe a interação com o chatbot.

    Parâmetros:
    \n\t`prompt (str)`: Texto da mensagem enviada pelo usuário.
    \n\t`mensagens (list)`: Lista contendo o histórico das mensagens da conversa.
    \n\t`flag (bool)`: Se `True`, exibe a mensagem visualmente no chat.
    \n\t`placeholder`: Elemento do Streamlit utilizado para atualizar mensagens em tempo real.

    Retorno:
    \n\t`None`: Atualiza o estado da sessão do Streamlit e exibe a interação.

    Exemplo:
    >>> mensagens = []
    >>> nova_mensagem("Olá!", mensagens, True)
    """
    st.session_state['show_modal'] = False

    nova_mensagem = {'role': 'user',
                     'content': prompt}

    mensagens.append(nova_mensagem)

    if flag:
        chat = st.chat_message(nova_mensagem['role'])
        chat.markdown(
            f'<div class="user-message">{nova_mensagem["content"]}</div>', unsafe_allow_html=True)

        chat = st.chat_message('assistant')

        placeholder = chat.empty()

        placeholder.markdown(
            "<div class='assistant-message'>▌ </div>", unsafe_allow_html=True)

    resposta_completa = ''

    try:
        respostas = retorna_resposta_modelo(
            mensagens,
            st.session_state['api_key'],
            modelo=st.session_state['modelo'],
            stream=True,
        )

        for resposta in respostas:
            try:
                json_resposta = json.loads(
                    resposta.lstrip("data: "))

                delta = json_resposta.get("choices", [{}])[
                    0].get("delta", {})

                content = delta.get("content", "")
                resposta_completa += content

                if flag:
                    placeholder.markdown(
                        f"<div class='assistant-message'>{resposta_completa}▌</div>",
                        unsafe_allow_html=True
                    )

            except json.JSONDecodeError as e:
                print("Mensagem de Stream recebida com sucesso!")
                continue

            except Exception as e:
                print(f"Erro inesperado: {e}")
                st.error(
                    "Erro inesperado ao processar a resposta.")

        if flag:
            placeholder.markdown(
                f"<div class='assistant-message'>{resposta_completa}</div>",
                unsafe_allow_html=True
            )

        nova_mensagem = {'role': 'assistant',
                         'content': resposta_completa}

        st.session_state['mensagens'] = mensagens

        mensagens.append(nova_mensagem)

        salvar_mensagens(mensagens)

        if placeholder is None:
            st.rerun()

    except requests.exceptions.HTTPError as e:
        st.error(
            '😣 Desculpe, mas o ChatGPT está indisponível no momento.')
        print(f"Erro HTTP: {e}")

    except Exception as e:
        st.error(
            '😫 Ocorreu um erro inesperado. Por favor, tente novamente mais tarde.')
        print(f"Erro inesperado: {e}")


def transcreve_audio(caminho_audio: str, prompt: str, headers: dict, _return: bool = True):
    """
    Transcreve um arquivo de áudio utilizando a API da OpenAI (Whisper-1).

    Parâmetros:
    \n\t`caminho_audio (str)`: Caminho do arquivo de áudio que será transcrito.
    \n\t`prompt (str)`: Sugestão opcional para orientar a transcrição.
    \n\t`headers (dict)`: Cabeçalhos HTTP contendo a chave da API e outras configurações.
    \n\t`_return (bool)`: Se `True`, exibe a transcrição no Streamlit; se `False`, apenas armazena no estado da sessão.

    Retorno:
    \n\t`str | None`: Retorna a transcrição do áudio se `_return` for `True`, ou `None` caso contrário.

    Exemplo:
    >>> headers = {"Authorization": "Bearer minha_api_key"}
    >>> transcricao = transcreve_audio("audio.mp3", "Transcreva este áudio.", headers)
    >>> print(transcricao)
    "Este é o conteúdo do áudio transcrito."
    """

    with open(caminho_audio, 'rb') as arquivo_audio:
        audio_bytes = arquivo_audio.read()
        # Preparar o MultipartEncoder (alternativo)
        # m = MultipartEncoder(
        #     fields={
        #         'file': ('audio.mp3', BytesIO(audio_bytes), 'audio/mpeg'),
        #         'prompt': prompt_input,
        #         'model': 'whisper-1',
        #         'language': 'pt',
        #         'response_format': 'text'
        #     }
        # )
        # headers['Content-Type'] = m.content_type
        files = {
            'file': ('audio.mp3', BytesIO(audio_bytes), 'audio/mpeg'),
            'model': (None, 'whisper-1'),
            'language': (None, 'pt'),
            'response_format': (None, 'text'),
            'prompt': (None, prompt)
        }

        response = requests.post(
            # "https://api.openai.com/v1/audio/transcriptions", headers=headers, data=m)
            "https://api.openai.com/v1/audio/transcriptions", headers=headers, files=files)

        try:
            if response.status_code == 200:
                transcricao = response.text
                st.session_state['transcricao'] = transcricao
                if _return:
                    return st.markdown(f'<div class="st-key-transcricao">{transcricao}</div><br/>', unsafe_allow_html=True)
                else:
                    return None

            else:
                print(f"Erro: {response.status_code}")
                print("Erro ao decodificar a resposta da API. Resposta:")
                print(response.text)
                return st.error(f"Erro: {response.status_code} ao decodificar a resposta da API. Veja os detalhes no terminal.")

        except ValueError:
            print(f"Erro: {response.status_code}")
            print("Erro ao decodificar a resposta da API. Resposta:")
            print(response.text)
            return st.error("Erro ao decodificar a resposta da API. Veja os detalhes no terminal.")


def adiciona_chunck_de_audio(frames_de_audio: list, chunck_audio) -> object:
    """
    Adiciona um conjunto de frames de áudio a um segmento de áudio existente.

    Parâmetros:
    \n\t`frames_de_audio (list)`: Lista de frames de áudio que serão adicionados ao segmento de áudio.
    \n\t`chunck_audio (pydub.AudioSegment)`: Segmento de áudio onde os frames serão concatenados.

    Retorno:
    \n\t`pydub.AudioSegment`: O segmento de áudio atualizado com os frames adicionados.

    Exemplo:
    >>> from pydub import AudioSegment
    >>> chunck_audio = AudioSegment.silent(duration=1000)  # Áudio de 1 segundo de silêncio
    >>> frames = [AudioSegment.silent(duration=500), AudioSegment.silent(duration=500)]
    >>> novo_audio = adiciona_chunck_de_audio(frames, chunck_audio)
    >>> print(len(novo_audio))
    2000  # O áudio agora tem 2 segundos de duração
    """
    for frame in frames_de_audio:
        sound = pydub.AudioSegment(
            data=frame.to_ndarray().tobytes(),
            sample_width=frame.format.bytes,
            frame_rate=frame.sample_rate,
            channels=len(frame.layout.channels)
        )
        chunck_audio += sound
    return chunck_audio


# TRANSCREVE VIDEO =====================================

def _salva_audio_do_video(video_bytes: BytesIO) -> str:
    """
    Extrai e salva o áudio de um arquivo de vídeo.

    Parâmetros:
    \n\t`video_bytes (BytesIO)`: Objeto contendo os bytes do vídeo a ser processado.

    Retorno:
    \n\t`str`: Retorna a string "Continue" após a extração do áudio ser concluída com sucesso.

    Exemplo:
    >>> with open("video.mp4", "rb") as f:
    >>>     video_bytes = BytesIO(f.read())
    >>> _salva_audio_do_video(video_bytes)
    "Continue"
    """
    with open(ARQUIVO_VIDEO_TEMP, mode='wb') as video_f:
        video_f.write(video_bytes.read())
    moviepy_video = VideoFileClip(str(ARQUIVO_VIDEO_TEMP))
    moviepy_video.audio.write_audiofile(str(ARQUIVO_AUDIO_TEMP))
    return "Continue"


@st.dialog("Enviar áudio por vídeo mp4")
def transcreve_video_recebido():
    """
    Transcreve o áudio de um vídeo enviado pelo usuário.

    Operações:
    \n\t- Exibe um campo para entrada de um prompt opcional.
    \n\t- Permite o upload de um arquivo de vídeo no formato `.mp4`.
    \n\t- Salva o áudio extraído do vídeo temporariamente.
    \n\t- Envia o áudio para transcrição utilizando a API da OpenAI (Whisper-1).
    \n\t- Exibe a transcrição resultante.

    Retorno:
    \n\t`None`: Apenas exibe a transcrição do áudio no Streamlit.

    Exemplo:
    >>> transcreve_video_recebido()
    """

    if st.session_state['api_key'] == '':
        st.error('Adicone uma chave de api na aba de configurações')
    else:
        headers = {
            "Authorization": f"Bearer {st.session_state['api_key']}"
        }
        prompt_video = st.text_input(
            '(opcional) Sugestão para orientar a transcrição.',
            key='input_video')
        st.info(
            "**Arraste e solte o arquivo no campo abaixo ou clique em 'Browse Files' para selecionar um arquivo.**")
        arquivo_video = st.file_uploader('Adicione um arquivo de vídeo .mp4', type=[
                                         'mp4'], label_visibility='collapsed')

        if arquivo_video is not None and st.session_state['transcricao'] == '':
            with st.spinner('Convertendo o vídeo para áudio...'):
                flag_continue = _salva_audio_do_video(arquivo_video)

            if not flag_continue is None and st.session_state['transcricao'] == '':
                with st.spinner('Processando o áudio...'):
                    st.info(
                        "Sua transcrição está sendo preparada para ser enviada!")
                    transcreve_audio(ARQUIVO_AUDIO_TEMP,
                                     prompt_video, headers, False)
                    flag_continue = None
                    arquivo_video = None

                    with st.spinner('Processando a resposta...'):
                        nova_mensagem(st.session_state['transcricao'],
                                      st.session_state['mensagens'],
                                      False,
                                      None)
                        st.rerun()

    if st.button("Fechar", key="Fechar"):
        js_debug("Botão Fechar")
        js_debug(st.session_state['transcricao'])
        arquivo_video = None
        st.session_state['transcricao'] = ''
        st.session_state['show_modal'] = False
        st.rerun()


# TRANSCREVE AUDIO =====================================

@st.dialog("Enviar áudio por arquivo mp3")
def transcreve_audio_recebido():
    """
    Transcreve um arquivo de áudio enviado pelo usuário.

    Operações:
    \n\t- Exibe um campo para entrada de um prompt opcional.
    \n\t- Permite o upload de um arquivo de áudio no formato `.mp3`.
    \n\t- Envia o áudio para transcrição utilizando a API da OpenAI (Whisper-1).
    \n\t- Exibe a transcrição resultante ou uma mensagem de erro, se necessário.

    Retorno:
    \n\t`None`: Apenas exibe a transcrição do áudio no Streamlit.

    Exemplo:
    >>> transcreve_audio_recebido()
    """
    if st.session_state['api_key'] == '':
        st.error('Adicone uma chave de api na aba de configurações')
    else:
        headers = {
            "Authorization": f"Bearer {st.session_state['api_key']}"
        }
        prompt_input = st.text_input(
            '(opcional) Sugestão para orientar a transcrição.',
            key='input_audio')
        st.info(
            "**Arraste e solte o arquivo no campo abaixo ou clique em 'Browse Files' para selecionar um arquivo.**")
        arquivo_audio = st.file_uploader('Adicione um arquivo de áudio .mp3', type=[
            'mp3'], label_visibility='collapsed')

        if arquivo_audio is not None and st.session_state['transcricao'] == '':
            audio_bytes = arquivo_audio.read()

            files = {
                'file': ('audio.mp3', BytesIO(audio_bytes), 'audio/mpeg'),
                'model': (None, 'whisper-1'),
                'language': (None, 'pt'),
                'response_format': (None, 'text'),
                'prompt': (None, prompt_input)
            }
            with st.spinner('Processando o áudio...'):
                response = requests.post(
                    "https://api.openai.com/v1/audio/transcriptions", headers=headers, files=files)

                try:
                    if response.status_code == 200:
                        st.info(
                            "Sua transcrição está sendo preparada para ser enviada!")
                        transcricao = response.text
                        st.session_state['transcricao'] = transcricao
                        arquivo_audio = None

                        with st.spinner('Processando a resposta...'):
                            nova_mensagem(transcricao,
                                          st.session_state['mensagens'],
                                          False,
                                          None)
                            st.rerun()

                    else:
                        st.error(
                            f"Erro: {response.status_code} ao decodificar a resposta da API. Veja os detalhes no terminal.")
                        print(f"Erro: {response.status_code}")
                        print("Erro ao decodificar a resposta da API. Resposta:")
                        print(response.text)

                except ValueError:
                    st.error(
                        "Erro ao decodificar a resposta da API. Veja os detalhes no terminal.")
                    print(f"Erro: {response.status_code}")
                    print("Erro ao decodificar a resposta da API. Resposta:")
                    print(response.text)
                    st.write(response.status_code)

        if st.button("Fechar", key="Fechar"):
            js_debug("Botão Fechar")
            js_debug(st.session_state['transcricao'])
            arquivo_audio = None
            st.session_state['transcricao'] = ''
            st.session_state['show_modal'] = False
            st.rerun()


def renderizar_mensagens(mensagens: list, placeholder=None) -> None:
    """
    Renderiza as mensagens da conversa na interface do Streamlit.

    Parâmetros:
    \n\t`mensagens (list)`: Lista contendo as mensagens a serem exibidas.
    \n\t`placeholder`: Elemento opcional do Streamlit para atualização dinâmica.

    Retorno:
    \n\t`None`: Apenas exibe as mensagens na interface.

    Exemplo:
    >>> mensagens = [
    >>>     {"role": "user", "content": "Olá!"},
    >>>     {"role": "assistant", "content": "Oi! Como posso te ajudar?"}
    >>> ]
    >>> renderizar_mensagens(mensagens)
    """
    for mensagem in mensagens:
        if mensagem['role'] == 'user':
            chat = st.chat_message(mensagem['role'])
            chat.markdown(
                f'<div class="user-message">{mensagem["content"]}</div>', unsafe_allow_html=True)
        elif mensagem['role'] == 'assistant' and placeholder is None:
            chat = st.chat_message(mensagens['role'])
            chat.markdown(
                f'<div class="assistant-message">{mensagens["content"]}</div>', unsafe_allow_html=True)
        if placeholder is not None:
            placeholder.markdown(
                "<div class='assistant-message'>▌</div>", unsafe_allow_html=True)


# PÁGINA PRINCIPAL ==================================================

def pg_conversas() -> None:
    """
    Exibe a interface principal do chat baseado em LLM (Large Language Model).

    Operações:
    \n\t- Exibe o cabeçalho do chat.
    \n\t- Carrega e renderiza as mensagens da conversa.
    \n\t- Exibe um campo de entrada de mensagens para interação do usuário.
    \n\t- Permite a seleção de diferentes formatos de entrada (texto, áudio, vídeo).
    \n\t- Gerencia a lógica de envio da mensagem e processamento da resposta.

    Retorno:
    \n\t`None`: Apenas exibe a interface e gerencia as interações no Streamlit.

    Exemplo:
    >>> pg_conversas()
    """
    st.header('🗨️ Chat de Conversas - LLM', divider=True)

    mensagens = ler_mensagens(st.session_state['mensagens'])

    placeholder = st.empty()

    for mensagem in mensagens:
        if mensagem['role'] == 'user':
            chat = st.chat_message(mensagem['role'])
            chat.markdown(
                f'<div class="user-message">{mensagem["content"]}</div>', unsafe_allow_html=True)
        else:
            chat = st.chat_message(mensagem['role'])
            chat.markdown(
                f'<div class="assistant-message">{mensagem["content"]}</div>', unsafe_allow_html=True)

    with st.container(key='footer'):
        prompt = st.chat_input('Fale com o tutor')

        options_pills = ["⌨️", "🎤", "📽️"]

        seleciona_midia = st.pills(
            "Selecione a Mídia",
            options_pills,
            selection_mode="single",
            key='input-select',
            label_visibility="hidden"
        )

        st.session_state['input'] = seleciona_midia

        js_debug(st.session_state['input'])

        # Verificar a seleção para abrir o diálogo correspondente
        if st.session_state['input'] == "⌨️":
            js_debug("reinicia o modal")
            # reseta
            st.session_state['show_modal'] = True
            st.session_state['transcricao'] = ''
        elif st.session_state['input'] == "🎤" and st.session_state['show_modal']:
            js_debug("transcreve_audio_recebido()")
            st.session_state['input'] = "⌨️"
            transcreve_audio_recebido()
        elif st.session_state['input'] == "📽️" and st.session_state['show_modal']:
            js_debug("transcreve_video_recebido()")
            st.session_state['input'] = "⌨️"
            transcreve_video_recebido()

        st.markdown(
            '_O Chat de Conversas pode cometer erros. Considere verificar informações importantes._')

        # Faz a requisição, se houver
        if prompt:
            if st.session_state['api_key'] == '':
                st.error('Adicone uma chave de api na aba de configurações')
            else:
                nova_mensagem(prompt, mensagens, True, placeholder)


# Página de Configurações =========================

def config_page() -> None:
    """
    Exibe a página de configurações do chatbot, permitindo modificar parâmetros do modelo de IA.

    Operações:
    \n\t- Exibe os campos de entrada para alteração do modelo de IA.
    \n\t- Permite modificar o tipo de busca e parâmetros de recuperação de informações.
    \n\t- Exibe e permite a edição do prompt base utilizado pelo chatbot.
    \n\t- Atualiza os valores na sessão do Streamlit e reinicia o chatbot se necessário.

    Retorno:
    \n\t`None`: Apenas exibe a interface e atualiza os valores de configuração no Streamlit.

    Exemplo:
    >>> config_page()
    """
    st.header('📑 - RAG Config', divider=True)

    model = st.text_input('Modifique o modelo',
                          value=get_config('modelo'))

    retrieval_search_type = st.text_input('Modifique o tipo de retrieval',
                                          value=get_config('retrieval_search_type'))

    retrieval_kwargs = st.text_input('Modifique os parâmetros de retrieval',
                                     value=json.dumps(get_config('retrieval_kwargs')))

    prompt = st.text_area('Modifique o prompt padrão',
                          height=300,
                          value=get_config('prompt'))

    if st.button('Salvar parâmetros', use_container_width=True):
        retrieval_kwargs = json.loads(retrieval_kwargs.replace("'", '"'))
        st.session_state['modelo'] = model
        st.session_state['retrieval_search_type'] = retrieval_search_type
        st.session_state['retrieval_kwargs'] = retrieval_kwargs
        st.session_state['prompt'] = prompt
        st.rerun()

    if st.button('Atualizar o ATI', use_container_width=True):
        if len(list(PASTA_ARQUIVOS.glob('*.pdf'))) == 0:
            st.error(
                'Adicione arquivos .pdf para inicializar o ATI (Agente Tutor Inteligente)')
        else:
            st.success('Inicializando o ATI (Agente Tutor Inteligente)...')
            cria_chain_conversa()
            st.rerun()


# Página de Tutoria =========================

def pg_tutoria() -> None:
    """
    Exibe a página de tutoria do chatbot, permitindo interações com documentos previamente carregados.

    Operações:
    \n\t- Exibe um cabeçalho e um aviso se nenhum documento for carregado.
    \n\t- Recupera o histórico de conversas do chatbot e exibe as mensagens.
    \n\t- Permite ao usuário interagir com o chatbot enviando novas mensagens.
    \n\t- Exibe respostas do chatbot com base nos documentos processados.

    Retorno:
    \n\t`None`: Apenas exibe a interface e processa as interações no Streamlit.

    Exemplo:
    >>> pg_tutoria()
    """
    st.header('🎓 ATI - Agente Tutor Inteligente', divider=True)

    if not 'chain' in st.session_state or st.session_state['chain'] == '':
        st.error('Faça o upload de PDFs para começar!')
    else:
        chain = st.session_state['chain']
        memory = chain.memory

        mensagens = memory.load_memory_variables({})['chat_history']

        container = st.container()
        for mensagem in mensagens:
            chat = container.chat_message(mensagem.type)
            chat.markdown(mensagem.content)

        nova_mensagem = st.chat_input(
            'Converse com o seu Agente Tutor Inteligente...')
        if nova_mensagem:
            chat = container.chat_message('human')
            chat.markdown(nova_mensagem)
            chat = container.chat_message('ai')
            chat.markdown('▌ ')  # Gerando resposta

            resposta = chain.invoke({'question': nova_mensagem})
            st.session_state['ultima_resposta'] = resposta
            st.rerun()


# Página de Análise =========================

def pg_analise() -> None:
    """
    Exibe a página de análise e depuração das interações do chatbot.

    Operações:
    \n\t- Exibe um cabeçalho para a seção de análise.
    \n\t- Recupera a última resposta gerada pelo chatbot.
    \n\t- Exibe o histórico de conversas e os documentos utilizados no contexto da resposta.
    \n\t- Mostra o prompt final gerado pelo modelo antes de processar a resposta.

    Retorno:
    \n\t`None`: Apenas exibe a interface e apresenta os detalhes da análise.

    Exemplo:
    >>> pg_analise()
    """

    st.header('📇 Página de debug', divider=True)

    prompt_template = get_config('prompt')
    prompt_template = PromptTemplate.from_template(prompt_template)

    if 'ultima_resposta' not in st.session_state or st.session_state['ultima_resposta'] == '':
        st.error('Realize uma pergunta para o modelo para visualizar o debug')
    else:
        ultima_resposta = st.session_state['ultima_resposta']

        contexto_docs = ultima_resposta['source_documents']
        contexto_list = [doc.page_content for doc in contexto_docs]
        contexto_str = '\n\n'.join(contexto_list)

        chain = st.session_state['chain']
        memory = chain.memory
        chat_history = memory.buffer_as_str

        with st.container(border=True):
            prompt = prompt_template.format(
                chat_history=chat_history,
                context=contexto_str,
                question=''
            )
            st.code(prompt)
