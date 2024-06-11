from main import config
import streamlit as st
import pandas as pd
from random import randint

config()

# Define a função para carregar as conexões existentes
def load_connections():
    # Verifica se há conexões na sessão
    if 'connections' not in st.session_state:
        st.session_state.connections = pd.DataFrame(columns=['id', 'name', 'connection_string'])

# Define a função para adicionar uma nova conexão
def add_connection(name, connection_string):
    load_connections()
    new_connection = {'id': randint(1000, 9999), 'name': name, 'connection_string': connection_string}
    st.session_state.connections = pd.concat([st.session_state.connections, pd.DataFrame([new_connection])], ignore_index=True)
    # Limpa os campos do formulário
    st.session_state.name = ""
    st.session_state.connection_string = ""

# Define a função para atualizar uma conexão existente
def update_connection(id, name, connection_string):
    load_connections()
    st.session_state.connections.loc[st.session_state.connections['id'] == id, 'name'] = name
    st.session_state.connections.loc[st.session_state.connections['id'] == id, 'connection_string'] = connection_string
    # Limpa os campos do formulário
    st.session_state.name = ""
    st.session_state.connection_string = ""

# Define a função para deletar uma conexão existente
def delete_connection(id):
    load_connections()
    st.session_state.connections = st.session_state.connections.drop(st.session_state.connections[st.session_state.connections['id'] == id].index)

# Define a função para testar uma conexão
def test_connection(connection_string):
    # Simula a conexão verificando se a string não está vazia
    return bool(connection_string)

# Define a função principal
def main():
    st.title("Gerenciador de Conexões de Banco de Dados")

    # Carrega as conexões existentes
    load_connections()

    # Exibe as conexões na tabela
    st.subheader("Conexões Existentes")
    st.dataframe(st.session_state.connections)

    # Operações CRUD
    st.subheader("Adicionar / Modificar / Deletar Conexão")

    operation = st.selectbox("Operação", ["Adicionar", "Modificar", "Deletar"])

    if operation in ["Adicionar", "Modificar"]:
        # Verifica se os campos do formulário estão na sessão
        if 'name' not in st.session_state:
            st.session_state.name = ""
        if 'connection_string' not in st.session_state:
            st.session_state.connection_string = ""

        # Input para o nome da conexão
        name = st.text_input("Nome da Conexão", st.session_state.name)
        st.session_state.name = name

        # Input para a connection string
        connection_string = st.text_input("Connection String", st.session_state.connection_string)
        st.session_state.connection_string = connection_string

    if operation == "Modificar":
        connection_id = st.selectbox("Selecionar Conexão para Modificar", st.session_state.connections['id'])

    if operation == "Deletar":
        connection_id = st.selectbox("Selecionar Conexão para Deletar", st.session_state.connections['id'])

    submit_button = st.button('Executar')

    if submit_button:
        if operation == "Adicionar":
            if test_connection(st.session_state.connection_string):
                add_connection(st.session_state.name, st.session_state.connection_string)
                st.success("Conexão adicionada com sucesso!")
            else:
                st.error("Falha ao adicionar conexão: Connection String inválida.")
        elif operation == "Modificar":
            if test_connection(st.session_state.connection_string):
                update_connection(connection_id, st.session_state.name, st.session_state.connection_string)
                st.success("Conexão modificada com sucesso!")
            else:
                st.error("Falha ao modificar conexão: Connection String inválida.")
        elif operation == "Deletar":
            delete_connection(connection_id)
            st.success("Conexão deletada com sucesso!")

        # Recarrega as conexões após qualquer operação CRUD
        load_connections()
        # Limpa a connection string
        st.session_state.connection_string = ""
        # Atualiza a página
        st.rerun()

# Executa a função principal
main()
