# main.py
import streamlit as st

from utils_openai import retorna_resposta_modelo
from utils_files import *

# INICIALIZAÇÃO ==================================================


def inicializacao():
    """
    Função para inicializar o estado da sessão com valores padrão.

    Esta função verifica se certas chaves de estado (`mensagens`, `conversa_atual`, `modelo`, `api_key`) existem no estado da sessão do Streamlit (`st.session_state`).
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


def tab_configuracoes(tab):
    """
    Função para configurar as opções do modelo e a chave da API em uma aba de configurações.

    Parâmetros:
    - `tab` (st.tabs.Tab): Um objeto de aba do Streamlit onde os elementos da interface de configuração serão exibidos.

    A função permite ao usuário selecionar o modelo a ser usado e adicionar a chave da API. Se a chave da API for alterada, ela será salva e uma mensagem de sucesso será exibida.
    """
    modelo_escolhido = tab.selectbox('Selecione o modelo',
                                     ['gpt-3.5-turbo', 'gpt-4'])
    st.session_state['modelo'] = modelo_escolhido

    chave = tab.text_input('Adicione sua api key',
                           value=st.session_state['api_key'])
    if chave != st.session_state['api_key']:
        st.session_state['api_key'] = chave
        salva_chave(chave)
        tab.success('Chave salva com sucesso')


# PÁGINA PRINCIPAL ==================================================


def pagina_principal():
    """
    Função para exibir a página principal do chatbot Asimov.

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
    mensagens = ler_mensagens(st.session_state['mensagens'])

    st.header('🎓 Agente Tutor Inteligente', divider=True)

    for mensagem in mensagens:
        if mensagem['role'] == 'user':
            chat = st.chat_message(mensagem['role'])
            chat.markdown(
                f'<div class="user-message">{mensagem["content"]}</div>', unsafe_allow_html=True)
        else:
            chat = st.chat_message(mensagem['role'])
            chat.markdown(
                f'<div class="assistant-message">{mensagem["content"]}</div>', unsafe_allow_html=True)

    prompt = st.chat_input('Fale com o chat')
    if prompt:
        if st.session_state['api_key'] == '':
            st.error('Adicone uma chave de api na aba de configurações')
        else:
            nova_mensagem = {'role': 'user',
                             'content': prompt}
            chat = st.chat_message(nova_mensagem['role'])
            chat.markdown(nova_mensagem['content'])
            mensagens.append(nova_mensagem)

            chat = st.chat_message('assistant')
            placeholder = chat.empty()
            placeholder.markdown("▌")
            resposta_completa = ''
            respostas = retorna_resposta_modelo(mensagens,
                                                st.session_state['api_key'],
                                                modelo=st.session_state['modelo'],
                                                stream=True)
            for resposta in respostas:
                resposta_completa += resposta.choices[0].delta.get(
                    'content', '')
                placeholder.markdown(resposta_completa + "▌")
            placeholder.markdown(resposta_completa)
            nova_mensagem = {'role': 'assistant',
                             'content': resposta_completa}
            mensagens.append(nova_mensagem)

            st.session_state['mensagens'] = mensagens
            salvar_mensagens(mensagens)


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
    # Aplicar tema escuro globalmente com CSS personalizado
    st.markdown('''
        <style>
            /* Cor de fundo da aplicação */
            .stApp { background-color: #000000 !important; color: #ffffff !important; }
            /* Cor de fundo da barra lateral */
            .stSidebar {background-color: rgb(38, 39, 48); color: #ffffff;}
            /* Cor do cabeçalho */
            header {background: rgb(14, 17, 23) !important;}
            /* Cor de fundo dos botões */
            .stButton > button { background-color: #3c3c3c; color: #ffffff; }
            /* Cor do texto do botão ao passar o mouse */
            .stButton button:hover { background-color: #5a5a5a !important; }
            /* Cor do texto do botão desabilitado */
            .stButton button:disabled { border-color: rgba(155, 155, 155, 0.4); color: rgba(155, 155, 155, 0.4);}
            /* Cor dos Labels*/
            label > div > p {color: #ffffff; }
            /* Cor dos Inputs*/
            .stSelectbox > div > div {color: color: rgb(250, 250, 250) !important; border-color: rgb(14,17,23) !important; background-color: rgb(14,17,23) !important;}
            /* Cor dos Selects*/
            .stTooltipHoverTarget > div > div, .st-dv, ul, li {color: color: rgb(250, 250, 250) !important; border-color: rgb(14,17,23) !important; background-color: rgb(14,17,23) !important;}
            input, .stTextInput > div > div > input {color: color: rgb(250, 250, 250) !important; border-color: rgb(14,17,23) !important; background-color: rgb(14,17,23) !important;}
            /* Outros ajustes de estilo conforme necessário */
            .stBottom, .stBottom > div {background-color: #0e1117 !important;}
            textarea {color: color: rgb(250, 250, 250) !important; border-color: rgb(14,17,23) !important; background-color: rgb(14,17,23) !important;}
            section > div > div > div > div > div > div {color: #ffffff !important;}
            .st-ep {caret-color: rgb(250, 250, 250);}
            .st-ei, .st-c1 {color: rgb(250, 250, 250);}
            /* Estilizar o fundo od emotions das mensagens */
            .user-message { color: white; padding: 10px; border-radius: 10px; margin-bottom: 10px; }
            .assistant-message { color: white; padding: 10px; border-radius: 10px; margin-bottom: 10px; }
            div[data-testid=\"stChatMessageAvatarUser\"] {background-color: rgb(108, 10, 10); }
            div[data-testid=\"stChatMessageAvatarAssistant\"] {background-color: rgb(10, 108, 10); }
        </style>
        ''', unsafe_allow_html=True)

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
