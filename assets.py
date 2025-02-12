# --- File: assets.py --- #

# --- Libraries --- #
# Permite a incorporação de elementos HTML e JavaScript personalizados.
import streamlit.components.v1 as components

# --- Attributes --- #
# Styles ==================================================
# Estilos CSS para personalizar a interface
css_styles = '''
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
            div[data-testid=\"stFileUploaderPagination\"] > small {color: #ffffff !important; }
            div[data-testid=\"stFileUploaderPagination\"] > div {color: #ffffff !important; }
            div[data-baseweb=\"tab-panel\"] > div[data-testid=\"stVerticalBlockBorderWrapper\"] {color: #ffffff !important; }
            div[data-baseweb=\"tab-panel\"] > div[data-testid=\"stVerticalBlockBorderWrapper\"] > div > div > div > div > div.stVerticalBlock > div > div > label[data-testid=\"stWidgetLabel\"] > div > p { color: #ffffff !important;}
            label > div > p {color: #ffffff !important; }
            /* Modals e Diálogos */
            .st-key-audio-input > div > label > div > p, .st-key-foto-input > div > label > div > p, div[aria-label=\"dialog\"] > div { color: #000000 !important;}
            div[aria-label=\"dialog\"] > div { color: #000000 !important;}
            div[data-testid=\"stVerticalBlockBorderWrapper\"] > div > div > div > div > div.stVerticalBlock > div > div > label[data-testid=\"stWidgetLabel\"] > div > p { color: #000000 !important;}
            button[aria-label=\"Close\"] { color: #000000 !important;}
            /* Textos dos rótulos de uploads dos arquivos*/
            .stFileUploaderFileName {color: #dddddd; }
            .stFileUploaderFileData > small {color: #aa0000; }
            /* Cor dos Inputs*/
            .stSelectbox > div > div {
                color: color: rgb(250, 250, 250) !important;
                border-color: rgb(14,17,23) !important;
                background-color: rgb(14,17,23) !important;
                -webkit-appearance: none;
                -moz-appearance: none;
                text-indent: 1px;
                text-overlow: '';
                }
            /* Cor dos Selects*/
            .stTooltipHoverTarget > div > div, .st-dv, ul, li {color: color: rgb(250, 250, 250); border-color: rgb(14,17,23); background-color: rgb(14,17,23) !important;}
            li[role=\"option\"] {background-color: rgb(14,17,23) !important;}
            input, .stTextInput > div > div > input {color: color: rgb(250, 250, 250) !important; border-color: rgb(14,17,23) !important; background-color: rgb(14,17,23) !important;}
            /* Outros ajustes de estilo conforme necessário */
            .stBottom, .stBottom > div {background-color: #0e1117 !important;}
            textarea {color: color: rgb(250, 250, 250) !important; border-color: rgb(14,17,23) !important; background-color: rgb(14,17,23) !important;}
            section > div > div > div > div > div > div {color: #ffffff !important;}
            .st-ep {caret-color: rgb(250, 250, 250);}
            .st-ei, .st-c1 {color: rgb(250, 250, 250);}
            /* Estilizar o fundo od emotions das mensagens */
            .user-message, .assistant-message, div[data-testid=\"stChatMessageContent\"] {
                color: white;
                padding: 10px;
                border-radius: 10px;
                margin-bottom: 10px;
                word-wrap: break-word; /* Quebra palavras longas */
            }

            .user-message, div[aria-label=\"Chat message from human\"] {
                background-color: rgba(240, 242, 246, 0.1); /* Fundo diferenciado */
            }

            .assistant-message, div[aria-label=\"Chat message from ai\"] {
                background-color: rgba(240, 242, 246, 0.2); /* Fundo diferenciado */
                margin-right: 1rem;
            }

            div[data-testid=\"stChatMessageAvatarUser\"] {background-color: rgb(108, 10, 10); }
            div[data-testid=\"stChatMessageAvatarAssistant\"] {background-color: rgb(10, 108, 10); }
            /* .stChatMessage:nth-child(odd) {background-color: rgba(240, 242, 246, 0.1);} */
            /* Remover para evitar inconsistências */
            .stChatMessage:nth-child(even) {
                background-color: rgba(240, 242, 246, 0.2);
            }
            .stChatMessage:nth-child(odd) {
                background-color: rgba(240, 242, 246, 0.1);
            }

            /* selectbox */
            .st-key-input-select {max-width: fit-content; width: fit-content; flex: unset; cursor: pointer;}
            .st-key-input-select > div.stSelectbox {cursor: pointer; width: 78px;}
            /* footer-container */
            .st-key-footer {
                position: fixed;
                bottom: 0;
                max-width: auto;
                margin: 0 0 5rem;
                border-radius: 10px;
                margin-bottom: 10px;
                display: flex;
                flex-direction: column;
                gap: 0px;
                background-color: rgba(155, 155, 155, 0.1);
                padding: 1rem;
            }

            .st-key-input {
                z-index: 100;
                /* max-width: 4rem; */
            }

            .stChatInput {
                max-width: 98%;
            }

            .stChatInput > div {
                max-width: 100%;
            }

            .st-key-footer > div > div > div > p > em {
                display: flex;
                justify-content: center;
            }

            .st-key-input > div > div > button {
                background-color: rgba(240, 242, 246, 0.1);
            }

            div[aria-label=\"dialog\"] {
                background-color: rgb(250, 250, 250) !important;
            }

        </style>
        '''

# JavaScripts ==================================================
# JavaScript de depuração para exibir logs no console do navegador
js_debug_script = """
<script>
// Log simples
console.log("script funcionando no front!");

// Outros tipos de log
console.warn("Aviso do script: isso é apenas um teste!");
console.error("Erro do script (apenas um teste)!");
console.info("Informação do script");
console.debug("Debug do script");

// Função de teste
function teste() {
    console.log("function teste aqui!");
    console.debug("Debug dentro da função teste");
    console.info("Info dentro da função teste");
}

teste();

// Evento DOMContentLoaded
document.addEventListener("DOMContentLoaded", () => {
    console.log("DOM fully loaded and parsed!");
});

// Evento no window.onload
window.addEventListener("load", () => {
    console.log("Window load event fired!");
});

// Log após um pequeno delay
setTimeout(() => {
    console.log("Testando log após 1 segundo!");
}, 1000);

</script>
"""

# --- Methods --- #


def js_debug(message='Olá Mundo!'):
    """
    Executa um script JavaScript de depuração para exibir mensagens no console do navegador.

    Parâmetros:
    \n\t`message (str)`: Mensagem a ser exibida no console do navegador.

    Exemplo:
    >>> js_debug("Teste de depuração")
    """
    components.html(f"""
    <script>
        // Executa js_debug
        console.log("js_debug", "{message}");
    </script>
    """, height=0)
