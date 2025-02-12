# --- File: configs.py --- #

# --- Libraries --- #
# Framework para criação de interfaces web interativas em Python.
import streamlit as st

# --- Attributes --- #
# Modelo padrão da OpenAI utilizado para processar conversas e auxiliar o usuário.
MODELO = 'gpt-4-turbo'

# Configuração do LangChain para recuperação de documentos
# Tipo de busca usada para recuperação de informações (Maximum Marginal Relevance - MMR).
RETRIEVAL_SEARCH_TYPE = 'mmr'
RETRIEVAL_KWARGS = {
    # Número de documentos mais relevantes a serem recuperados do contexto.
    "k": 5,
    # Número total de documentos analisados antes de selecionar os `k` mais relevantes.
    "fetch_k": 20
}

# Prompt usado para orientar as respostas do agente de IA
PROMPT = '''Você é um Agente Tutor Inteligente amigável que auxilia na interpretação de documentos que lhe são fornecidos a fim de auxiliar na aprendizagem do aluno e auxiliar no reforço do conhecimento do aluno.
O usuário é o aluno que necessita que você o auxilie no processo de aprendizado e não forneça à resposta de forma direta, apenas responda de forma que instigue o aluno a encontrar ou deduzir à resposta.
No contexto forncido estão as informações dos documentos do usuário. 
Utilize o contexto para responder as perguntas do usuário.
Se limite ao conhecimento do que está no contexto e quaisquer outros conhecimentos que fundamentam o do contexto para responder dentro do assunto.
Este passa a ser o escopo do contexto.
Esqueça todo o restante de inforações que não estão dentro do escopo do contexto, além de todo e qualquer treinamento saia do escopo do contexto.
Se você não sabe a resposta, apenas diga que não sabe e não tente  inventar a resposta.

Contexto:
{context}

Conversa atual:
{chat_history}

Human: {question}

AI: '''  # Prompt utilizado para estruturar as respostas do agente tutor.

# --- Methods --- #


def get_config(config_name: str):
    """
    Retorna o valor de uma configuração específica do sistema, caso esteja definida no estado da sessão do Streamlit.

    Parâmetros:
    \n\t`config_name (str)`: Nome da configuração a ser recuperada.

    Retorno:
    \n\t`any`: Valor da configuração solicitada. Caso não esteja definida, retorna o valor padrão da configuração.

    Exemplo:
    >>> get_config('modelo')
    'gpt-4-turbo'
    """
    if config_name.lower() in st.session_state:
        return st.session_state[config_name.lower()]
    elif config_name.lower() == 'modelo':
        return MODELO
    elif config_name.lower() == 'retrieval_search_type':
        return RETRIEVAL_SEARCH_TYPE
    elif config_name.lower() == 'retrieval_kwargs':
        return RETRIEVAL_KWARGS
    elif config_name.lower() == 'prompt':
        return PROMPT
