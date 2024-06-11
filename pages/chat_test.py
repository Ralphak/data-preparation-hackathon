import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats

from app.gemini_connection import send_prompt_to_gemini

# Função para realizar a pré-análise dos dados usando Pandas
def pre_analysis(df):
    analysis_results = {}
    analysis_results['missing_values'] = df.isnull().sum()
    analysis_results['inconsistent_dates'] = df.apply(lambda col: pd.to_datetime(col, errors='coerce', format='%Y/%m/%d').isnull().sum() if col.dtype == 'object' else 0)
    analysis_results['duplicate_rows'] = df.duplicated().sum()
    analysis_results['invalid_values'] = df.apply(lambda col: (col < 0).sum() if np.issubdtype(col.dtype, np.number) else 0)
    analysis_results['invalid_numeric'] = df.apply(lambda col: pd.to_numeric(col, errors='coerce').isnull().sum() if col.dtype == 'object' else 0)
    z_scores = np.abs(stats.zscore(df.select_dtypes(include=[np.number])))
    analysis_results['outliers'] = (z_scores > 3).sum().sum()
    return analysis_results

# Carregar dados de exemplo
df = pd.DataFrame({
    'data': ['2022/01/01', '2022-02-30', '2023/03/03', None, '2023-04-04'],
    'preco': [100, 200, 'trezentos', 400, None],
    'idade': [25, -5, 30, 40, None],
    'nome': ['Alice', 'Bob', 'Alice', 'Eve', 'Alice'],
    'salario': [50000, 120000, 1300000, 45000, 47000]
})

# Análise prévia dos dados
analysis_results = pre_analysis(df)

# Função para exibir os resultados da pré-análise em formato de texto
def analysis_results_text(analysis_results):
    text = (
        "### Resultados da Pré-Análise dos Dados\n"
        "1. **Valores Faltantes:**\n"
        f"{analysis_results['missing_values']}\n\n"
        "2. **Inconsistências de Formato:**\n"
        f"{analysis_results['inconsistent_dates']}\n\n"
        "3. **Duplicatas:**\n"
        f"{analysis_results['duplicate_rows']}\n\n"
        "4. **Valores Fora do Padrão:**\n"
        f"{analysis_results['invalid_values']}\n\n"
        "5. **Valores Inválidos:**\n"
        f"{analysis_results['invalid_numeric']}\n\n"
        "6. **Outliers:**\n"
        f"{analysis_results['outliers']}\n\n"
        "Por favor, indique qual problema você deseja tratar primeiro."
    )
    return text

# Inicializa a sessão de chat
if 'messages' not in st.session_state:
    st.session_state['messages'] = []
    initial_message = analysis_results_text(analysis_results)
    st.session_state['messages'].append({'role': 'IA', 'content': initial_message})

# Função para adicionar uma mensagem
def add_message(role, content):
    st.session_state['messages'].append({'role': role, 'content': content})

# Função para gerar o prompt específico com base na escolha do usuário
def generate_prompt_for_issue(issue, analysis_results):
    if issue == "Valores Faltantes":
        prompt = (
            f"Você escolheu tratar valores faltantes. Aqui estão as colunas com valores faltantes:\n"
            f"{analysis_results['missing_values']}\n"
            "Por favor, indique como você deseja preencher esses valores (ex: com um valor padrão, com a média da coluna, etc.)."
        )
    elif issue == "Inconsistências de Formato":
        prompt = (
            f"Você escolheu tratar inconsistências de formato. Aqui estão as colunas com inconsistências de formato:\n"
            f"{analysis_results['inconsistent_dates']}\n"
            "Por favor, indique como você deseja padronizar esses formatos (ex: padronizar para 'YYYY/MM/DD', etc.)."
        )
    elif issue == "Duplicatas":
        prompt = (
            f"Você escolheu tratar duplicatas. Há {analysis_results['duplicate_rows']} linhas duplicadas.\n"
            "Por favor, indique como você deseja tratar essas duplicatas (ex: remover duplicatas, manter apenas a primeira ocorrência, etc.)."
        )
    elif issue == "Valores Fora do Padrão":
        prompt = (
            f"Você escolheu tratar valores fora do padrão. Aqui estão os valores fora do padrão:\n"
            f"{analysis_results['invalid_values']}\n"
            "Por favor, indique como você deseja tratar esses valores (ex: corrigir manualmente, preencher com 0, etc.)."
        )
    elif issue == "Valores Inválidos":
        prompt = (
            f"Você escolheu tratar valores inválidos. Aqui estão as colunas com valores inválidos:\n"
            f"{analysis_results['invalid_numeric']}\n"
            "Por favor, indique como você deseja tratar esses valores (ex: converter texto em números, etc.)."
        )
    elif issue == "Outliers":
        prompt = (
            f"Você escolheu tratar outliers. Há {analysis_results['outliers']} outliers detectados.\n"
            "Por favor, indique como você deseja tratar esses outliers (ex: revisar manualmente, ajustar para valores dentro do intervalo esperado, etc.)."
        )
    return prompt

# Layout principal da página
st.title("Chatbot de Correção de Dados")

# Botão para abrir o modal de chat
if st.button("Abrir Chat"):
    st.session_state['modal'] = True

# Exibir modal de chat se ativado
if 'modal' in st.session_state and st.session_state['modal']:
    with st.expander("Chat com a IA", expanded=True):
        
        # Exibir mensagens
        for message in st.session_state['messages']:
            st.write(f"**{message['role']}:** {message['content']}")

        # Caixa de entrada de texto
        user_input_container = st.empty()
        user_input = user_input_container.text_input("Você:", key="user_input")

        # Enviar mensagem
        if st.button("Enviar"):
            if user_input:
                add_message("Usuário", user_input)
                # Gerar e enviar prompt específico para o Gemini com base na escolha do usuário
                response = send_prompt_to_gemini(generate_prompt_for_issue(user_input, analysis_results))
                if response:
                    add_message("IA", response)
                # Limpar a entrada de texto
                user_input_container.text_input("Você:", value="", key="user_input")

        # Botão para fechar o chat
        if st.button("Fechar Chat"):
            st.session_state['modal'] = False
