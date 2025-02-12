# --- File: main.py --- #

# --- Libraries --- #
# Importa todas as funções e classes do módulo utils_openai, que provavelmente contém funcionalidades relacionadas à API da OpenAI.
from utils_openai import *
# Importa todas as funções e classes do módulo utils_files, que possivelmente gerencia arquivos locais e manipulação de dados.
from utils_files import *

# --- Attributes --- #
# `st.session_state`: Dicionário que armazena variáveis de estado ao longo da execução da aplicação Streamlit.
# Os seguintes atributos são inicializados na sessão:
# - `mensagens`: Lista de mensagens da conversa atual.
# - `conversa_atual`: Nome da conversa ativa.
# - `ultima_resposta`: Última resposta gerada pelo chatbot.
# - `chain`: Armazena a cadeia de conversação ativa.
# - `modelo`: Define o modelo de IA usado (padrão: 'gpt-4-turbo').
# - `api_key`: Chave da API para autenticação com a OpenAI.
# - `theme`: Tema da interface ('dark' ou 'light').
# - `transcricao_mic`: Texto transcrito do microfone.
# - `transcricao`: Texto transcrito geral.
# - `show_modal`: Define se o modal inicial será exibido.

# --- Methods --- #
# INICIALIZAÇÃO ==================================================


def inicializacao():
    """
    Inicializa as variáveis de estado da sessão do Streamlit, garantindo que existam para evitar erros durante a execução do programa.
    """
    if not 'mensagens' in st.session_state:
        st.session_state.mensagens = []
    if not 'conversa_atual' in st.session_state:
        st.session_state.conversa_atual = ''
    if not 'ultima_resposta' in st.session_state:
        st.session_state.ultima_resposta = ''
    if not 'chain' in st.session_state:
        st.session_state.chain = ''
    if not 'modelo' in st.session_state:
        st.session_state.modelo = 'gpt-4-turbo'
    if not 'api_key' in st.session_state:
        # Obtém a chave da API através da função 'le_chave()'.
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
    Exibe a aba de conversas no Streamlit, permitindo criar novas conversas e listar as existentes.

    Parâmetros:
    \n\t`tab (streamlit.tabs)`: Objeto da aba onde a interface será renderizada.
    """
    tab.button('➕ Nova conversa',
               on_click=seleciona_conversa,
               args=('', ),
               use_container_width=True)
    tab.markdown('')
    conversas = listar_conversas()
    for nome_arquivo in conversas:
        nome_mensagem = desconverte_nome_mensagem(
            nome_arquivo).capitalize()
        if len(nome_mensagem) == 30:
            nome_mensagem += '...'
        tab.button(nome_mensagem,
                   on_click=seleciona_conversa,
                   args=(nome_arquivo, ),
                   disabled=nome_arquivo == st.session_state['conversa_atual'],
                   use_container_width=True)


def tab_configuracoes(tab):
    """
    Exibe a aba de configurações, permitindo selecionar o modelo de IA e inserir a chave da API.

    Parâmetros:
    \n\t`tab (streamlit.tabs)`: Objeto da aba onde a interface será renderizada.
    """
    modelo_escolhido = tab.selectbox('Selecione o modelo',
                                     ['gpt-4-turbo',
                                         'gpt-4o',
                                         'gpt-4',
                                         'gpt-3.5-turbo'],
                                     key='label-select')
    st.session_state['modelo'] = modelo_escolhido

    chave = tab.text_input('Adicione sua api key',
                           value=st.session_state['api_key'], key="key")

    if chave != st.session_state['api_key']:
        st.session_state['api_key'] = chave
        salva_chave(chave)
        tab.success('Chave salva com sucesso')


def tab_tutoria(tab):
    """
    Exibe a aba de tutoria, permitindo o upload de arquivos PDF e inicialização do chatbot.

    Parâmetros:
    \n\t`tab (streamlit.tabs)`: Objeto da aba onde a interface será renderizada.
    """

    tab.markdown('Tab de Tutoria')

    with tab.container():
        uploaded_pdfs = st.file_uploader(
            'Adicione seus arquivos de documento .pdf',
            type=['.pdf'],
            accept_multiple_files=True
        )
        if not uploaded_pdfs is None:
            for arquivo in PASTA_ARQUIVOS.glob('*.pdf'):
                arquivo.unlink()
            for pdf in uploaded_pdfs:
                with open(PASTA_ARQUIVOS / pdf.name, 'wb') as f:
                    f.write(pdf.read())

    label_botao = 'Inicializar o ATI'
    if 'chain' in st.session_state:
        label_botao = 'Atualizar o ATI'
    if tab.button(label_botao, use_container_width=True, key='chatbot-btn'):
        if len(list(PASTA_ARQUIVOS.glob('*.pdf'))) == 0:
            st.error('Adicione arquivos .pdf para inicializar o ATI')
        else:
            st.success('Inicializando o ATI...')
            cria_chain_conversa()
            st.rerun()


def tab_analise(tab):
    """
    Exibe a aba de análise de documentos.

    Parâmetros:
    \n\t`tab (streamlit.tabs)`: Objeto da aba onde a interface será renderizada.
    """

    tab.markdown('📇 Tab de análise')


# MAIN ==================================================
st.set_page_config(page_title="Agente Tutor Inteligente",
                   page_icon="🎓",
                   layout="wide",
                   initial_sidebar_state="expanded",)


def main():
    """
    Função principal que inicializa a interface do Streamlit e distribui o conteúdo nas abas.
    """
    inicializacao()
    # Aplicando a folha de estilo ao documento
    st.markdown(css_styles, unsafe_allow_html=True)

    if st.session_state['theme'] == 'dark':
        st.markdown(
            '<style>.stApp { background-color: black; color: white; color-scheme: dark;}</style>', unsafe_allow_html=True)
    else:
        st.markdown(
            '<style>.stApp { background-color: white; }</style>', unsafe_allow_html=True)

    # Recurso técnico para um problema de renderização de mais de um tipo de ambiente de trabalho nas abas do streamlit@1.40.0 (versão atual durante o desenvolvimento) que encontrei
    tabs = st.tabs(["Conversas", "Configurações", "Tutoria", "Análise"])
    with st.sidebar:
        tab1, tab2, tab3, tab4 = st.tabs(["Conversas",
                                          "Configurações",
                                          "Tutoria",
                                          "Análise"])

    with tabs[0]:
        tab_conversas(tab1)
        pg_conversas()

    with tabs[1]:
        tab_configuracoes(tab2)
        config_page()

    with tabs[2]:
        tab_tutoria(tab3)
        pg_tutoria()

    with tabs[3]:
        tab_analise(tab4)
        pg_analise()


if __name__ == '__main__':
    main()
