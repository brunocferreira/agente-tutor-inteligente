# main.py
import requests
import pydub
import streamlit as st
import json

from utils_openai import *
from utils_files import *
from assets import *

from moviepy import *
from io import BytesIO


# INICIALIZAÇÃO ==================================================

def inicializacao():
    """
    Função para inicializar o estado da sessão com valores padrão.

    Esta função verifica se certas chaves de estado (`mensagens`, `conversa_atual`, `modelo`, `api_key`, `theme`, `transcricao_mic`) existem no estado da sessão do Streamlit (`st.session_state`).
    Se não existirem, são inicializadas com valores padrão.

    Parâmetros:
    - Nenhum.

    Retorna:
    - Nenhum. Atualiza o estado da sessão com valores padrão se as chaves não existirem.
    """
    if not 'mensagens' in st.session_state:
        st.session_state.mensagens = []
    if not 'conversa_atual' in st.session_state:
        st.session_state.conversa_atual = ''
    if not 'modelo' in st.session_state:
        st.session_state.modelo = 'gpt-3.5-turbo'
    if not 'api_key' in st.session_state:
        st.session_state.api_key = le_chave()
    if not 'theme' in st.session_state:
        st.session_state.theme = 'dark'
    if not 'transcricao_mic' in st.session_state:
        st.session_state['transcricao_mic'] = ''
    if 'transcricao' not in st.session_state:
        st.session_state['transcricao'] = ''
    if 'show_modal' not in st.session_state:
        st.session_state['show_modal'] = True


# TABS ==================================================

def tab_conversas(tab):
    """
    Função para exibir um painel de conversas em uma aba de interface gráfica.

    Parâmetros:
    - `tab` (st.tabs.Tab): Um objeto de aba do Streamlit onde os elementos da interface serão exibidos.

    Esta função cria um botão para iniciar uma nova conversa e lista as conversas existentes. Cada conversa é exibida como um botão que, quando clicado, seleciona a conversa correspondente.
    Conversas já selecionadas são desabilitadas.
    """
    tab.button('➕ Nova conversa',
               on_click=seleciona_conversa,
               args=('', ),
               use_container_width=True)
    tab.markdown('')
    conversas = listar_conversas()
    for nome_arquivo in conversas:
        nome_mensagem = desconverte_nome_mensagem(nome_arquivo).capitalize()
        if len(nome_mensagem) == 30:
            nome_mensagem += '...'
        tab.button(nome_mensagem,
                   on_click=seleciona_conversa,
                   args=(nome_arquivo, ),
                   disabled=nome_arquivo == st.session_state['conversa_atual'],
                   use_container_width=True)


def tab_configuracoes(tab):
    """
    Função para configurar as opções do modelo e a chave da API em uma aba de configurações.

    Parâmetros:
    - `tab` (st.tabs.Tab): Um objeto de aba do Streamlit onde os elementos da interface de configuração serão exibidos.

    A função permite ao usuário selecionar o modelo a ser usado e adicionar a chave da API. Se a chave da API for alterada, ela será salva e uma mensagem de sucesso será exibida.
    """
    modelo_escolhido = tab.selectbox('Selecione o modelo',
                                     ['gpt-3.5-turbo', 'gpt-4'],
                                     key='label-select')
    st.session_state['modelo'] = modelo_escolhido

    chave = tab.text_input('Adicione sua api key',
                           value=st.session_state['api_key'], key="key")

    if chave != st.session_state['api_key']:
        st.session_state['api_key'] = chave
        salva_chave(chave)
        tab.success('Chave salva com sucesso')

    tab.button('➕ Inserir filtro',
               on_click=seleciona_conversa,
               args=('', ),
               use_container_width=True)


# FUNÇÕES ==================================================

def seleciona_conversa(nome_arquivo):
    """
    Função para selecionar uma conversa e atualizar o estado da sessão.

    Parâmetros:
    - `nome_arquivo` (str): O nome do arquivo contendo a conversa. Se o valor for uma string vazia, inicia uma nova conversa.

    A função atualiza o estado da sessão (`st.session_state`) com a conversa selecionada ou uma nova conversa se `nome_arquivo` for vazio.
    """
    if nome_arquivo == '':
        st.session_state['mensagens'] = []
    else:
        mensagem = ler_mensagem_por_nome_arquivo(nome_arquivo)
        st.session_state['mensagens'] = mensagem
    st.session_state['conversa_atual'] = nome_arquivo


def mascarar_chave(chave):
    if len(chave) > 10:
        return chave[:5] + '***' + chave[-5:]
    else:
        return chave


def nova_mensagem(prompt, mensagens, flag=False, placeholder=None):
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


def transcreve_audio(caminho_audio, prompt, headers, _return=True):
    """
    Função para transcrever um arquivo de áudio usando o modelo Whisper-1.

    Parâmetros:
    - `caminho_audio` (str): O caminho para o arquivo de áudio que será transcrito.
    - `prompt` (str): Um prompt opcional para orientar a transcrição.

    Operações:
    - Abre o arquivo de áudio no modo binário de leitura.
    - Envia o arquivo de áudio e o prompt para a API de transcrição do cliente.
    - Especifica o modelo 'whisper-1' e o idioma 'pt' (português) para a transcrição.
    - Define o formato da resposta como 'text'.

    Retorna:
    - `transcricao` (str): O texto transcrito do arquivo de áudio.
    """

    with open(caminho_audio, 'rb') as arquivo_audio:
        audio_bytes = arquivo_audio.read()
        # Preparar o MultipartEncoder
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
                    return st.markdown( f'<div class="st-key-transcricao">{transcricao}</div><br/>', unsafe_allow_html=True)
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


def adiciona_chunck_de_audio(frames_de_audio, chunck_audio):
    """
    Função para adicionar um conjunto de frames de áudio a um segmento de áudio existente.

    Parâmetros:
    - `frames_de_audio` (list): Uma lista de frames de áudio que serão adicionados ao segmento.
    - `chunck_audio` (pydub.AudioSegment): O segmento de áudio ao qual os frames serão adicionados.

    Operações:
    - Itera sobre cada frame na lista `frames_de_audio`.
    - Converte cada frame em um segmento de áudio do pydub usando `AudioSegment`.
    - Adiciona o segmento de áudio convertido ao `chunck_audio` existente.

    Retorna:
    - `chunck_audio` (pydub.AudioSegment): O segmento de áudio atualizado com os frames adicionados.
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

def _salva_audio_do_video(video_bytes):
    """
    Função para extrair e salvar o áudio de um arquivo de vídeo.

    Parâmetros:
    - `video_bytes` (io.BytesIO): O objeto de bytes do vídeo que será processado.

    Operações:
    - Abre um arquivo temporário para salvar o vídeo recebido.
    - Escreve os bytes do vídeo no arquivo temporário.
    - Carrega o vídeo temporário utilizando o MoviePy.
    - Extrai a faixa de áudio do vídeo e salva em um arquivo de áudio temporário.

    Retorna:
    - Nenhum.
    """
    with open(ARQUIVO_VIDEO_TEMP, mode='wb') as video_f:
        video_f.write(video_bytes.read())
    moviepy_video = VideoFileClip(str(ARQUIVO_VIDEO_TEMP))
    moviepy_video.audio.write_audiofile(str(ARQUIVO_AUDIO_TEMP))
    return "Continue"


@st.dialog("Enviar áudio por vídeo mp4")
def transcreve_video_recebido():
    """
    Função para transcrever o áudio de um vídeo enviado pelo usuário.

    Operações:
    - Exibe um campo de entrada de texto para um prompt opcional.
    - Permite ao usuário carregar um arquivo de vídeo no formato .mp4.
    - Se um arquivo de vídeo for carregado, salva o áudio do vídeo em um arquivo temporário.
    - Transcreve o áudio do arquivo de vídeo utilizando um modelo de transcrição.
    - Exibe a transcrição do áudio para o usuário.

    Parâmetros:
    - Nenhum.

    Retorna:
    - Nenhum. Exibe a transcrição do áudio para o usuário.
    """

    if st.session_state['api_key'] == '':
        st.error('Adicone uma chave de api na aba de configurações')
    else:
        headers = {
            "Authorization": f"Bearer {st.session_state['api_key']}"
        }
        prompt_video = st.text_input(
            '(opcional) Digite o seu prompt',
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
                    # st.info( "Sua transcrição está sendo preparada para você **Copiar** e **Fechar** para então **Colar** em **Fale com o tutor**")
                    st.info( "Sua transcrição está sendo preparada para ser enviada!")
                    transcreve_audio(ARQUIVO_AUDIO_TEMP, prompt_video, headers, False)
                    # st.success( "Sua transcrição está pronta!")
                    # st.warning( "Após colar a transcrição, revise o texto dela antes de enviar a sua solicitação.😉")
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
    Função para transcrever um arquivo de áudio enviado pelo usuário.

    Operações:
    - Exibe um campo de entrada de texto para um prompt opcional.
    - Permite ao usuário carregar um arquivo de áudio no formato .mp3.
    - Se um arquivo de áudio for carregado, lê seu conteúdo como bytes.
    - Envia o arquivo de áudio e o prompt opcional para a API de transcrição do OpenAI.
    - Especifica o modelo 'whisper-1' e o idioma 'pt' (português) para a transcrição.
    - Define o formato da resposta como 'text'.
    - Exibe a transcrição do áudio ou uma mensagem de erro caso a transcrição falhe.

    Parâmetros:
    - Nenhum.

    Retorna:
    - Nenhum. Exibe a transcrição do áudio ou uma mensagem de erro para o usuário.
    """
    if st.session_state['api_key'] == '':
        st.error('Adicone uma chave de api na aba de configurações')
    else:
        headers = {
            "Authorization": f"Bearer {st.session_state['api_key']}"
        }
        prompt_input = st.text_input(
            '(opcional) Digite o seu prompt',
            key='input_audio')
        st.info(
            "**Arraste e solte o arquivo no campo abaixo ou clique em 'Browse Files' para selecionar um arquivo.**")
        arquivo_audio = st.file_uploader('Adicione um arquivo de áudio .mp3', type=[
            'mp3'], label_visibility='collapsed')

        if arquivo_audio is not None and st.session_state['transcricao'] == '':
            audio_bytes = arquivo_audio.read()
            # Preparar o MultipartEncoder
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
                'prompt': (None, prompt_input)
            }
            with st.spinner('Processando o áudio...'):
                response = requests.post(
                    # "https://api.openai.com/v1/audio/transcriptions", headers=headers, data=m)
                    "https://api.openai.com/v1/audio/transcriptions", headers=headers, files=files)

                try:
                    if response.status_code == 200:
                        # st.info( "Sua transcrição está sendo preparada para você **Copiar** e **Fechar** para então **Colar** em **Fale com o tutor**")
                        st.info( "Sua transcrição está sendo preparada para ser enviada!")
                        transcricao = response.text
                        st.session_state['transcricao'] = transcricao
                        # st.markdown( f'<div class="st-key-transcricao">{transcricao}</div><br/>', unsafe_allow_html=True)
                        # st.success( "Sua transcrição está pronta!")
                        # st.warning( "Após colar a transcrição, revise o texto dela antes de enviar a sua solicitação.😉")
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


def renderizar_mensagens(mensagens, placeholder=None):
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

def pagina_principal():
    """
    Função para exibir a página principal do chat com o Agente Tutor Inteligente.

    Esta função configura a interface do chatbot, exibe mensagens anteriores,
    gerencia a entrada do usuário e chama o modelo para obter respostas.

    Fluxo da Função:
    - Lê as mensagens salvas do estado da sessão.
    - Exibe o cabeçalho da aplicação.
    - Itera sobre as mensagens e exibe cada uma delas.
    - Configura uma caixa de entrada para o usuário digitar novas mensagens.
    - Verifica se uma chave da API está disponível antes de processar a nova mensagem.
    - Envia a mensagem do usuário para o modelo e exibe a resposta gerada.

    Parâmetros:
    - Nenhum.

    Retorna:
    - Nenhum. Atualiza o estado da sessão e a interface do usuário.
    """

    st.header('🎓 Agente Tutor Inteligente', divider=True)

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
        # reseta
        st.session_state['show_modal'] = True
    elif st.session_state['input'] == "🎤" and st.session_state['show_modal']:
        js_debug("transcreve_audio_recebido()")
        st.session_state['input'] = "⌨️"
        # gravacao_audio()
        transcreve_audio_recebido()
    elif st.session_state['input'] == "📽️" and st.session_state['show_modal']:
        js_debug("transcreve_video_recebido()")
        st.session_state['input'] = "⌨️"
        # upload_video()
        transcreve_video_recebido()

    # Faz a requisição se houver
    if prompt:
        if st.session_state['api_key'] == '':
            st.error('Adicone uma chave de api na aba de configurações')
        else:
            nova_mensagem(prompt, mensagens, True, placeholder)


# MAIN ==================================================
st.set_page_config(page_title="Agente Tutor Inteligente",
                   page_icon="🎓",
                   layout="wide",
                   initial_sidebar_state="expanded",)


def main():
    """
    Função principal para executar a aplicação de chatbot.

    Esta função realiza a inicialização do estado da sessão, configura a página principal do chatbot,
    e cria abas laterais para navegação entre conversas e configurações.

    Parâmetros:
    - Nenhum.

    Retorna:
    - Nenhum. Configura a interface do usuário e o estado da sessão.
    """
    inicializacao()
    st.markdown(css_styles, unsafe_allow_html=True)

    pagina_principal()
    tab1, tab2 = st.sidebar.tabs(['Conversas', 'Configurações'])
    tab_conversas(tab1)
    tab_configuracoes(tab2)
    if st.session_state['theme'] == 'dark':
        st.markdown(
            '<style>.stApp { background-color: black; color: white; color-scheme: dark;}</style>', unsafe_allow_html=True)
    else:
        st.markdown(
            '<style>.stApp { background-color: white; }</style>', unsafe_allow_html=True)


if __name__ == '__main__':
    main()
