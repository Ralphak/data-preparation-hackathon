from main import config
import pandas as pd
import streamlit as st
import mysql.connector

config()

# Define a função principal
def _main():
    st.title("Gerenciador de Conexões de Banco de Dados")

    # Função para conectar ao banco de dados MySQL
    @st.cache_resource
    def connect_to_database(db_host, db_port, db_name, db_user, db_pass):
        try:
            # Conecta ao banco de dados MySQL
            conn = mysql.connector.connect(
                host=db_host,
                port=db_port,
                database=db_name,
                user=db_user,
                password=db_pass
            )
            st.success("Conexão bem-sucedida ao banco de dados MySQL!")
            return conn
        except Exception as e:
            st.error(f"Erro ao conectar ao banco de dados: {e}")

    # Função para buscar os dados da tabela
    def fetch_table_data(conn, table_name):
        try:
            # Obtém os dados da tabela selecionada
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {table_name}")
            data = cursor.fetchall()
            if data:
                df = pd.DataFrame(data, columns=[i[0] for i in cursor.description])
                return df
            else:
                st.warning(f"Nenhum dado encontrado na tabela {table_name}.")
        except Exception as e:
            st.error(f"Erro ao obter dados da tabela: {e}")
        finally:
            cursor.close()  # Fecha o cursor

    # Input de texto para os parâmetros de conexão do banco de dados MySQL
    db_host = st.text_input("DB Host", "***REMOVED***")
    db_port = st.text_input("DB Port", "***REMOVED***")
    db_name = st.text_input("DB Name", "***REMOVED***")
    db_user = st.text_input("DB User", "***REMOVED***")
    db_pass = st.text_input("DB Password", "***REMOVED***", type="password")
    
    # Botão para conectar ao banco de dados
    if st.button("Conectar ao Banco de Dados"):
        # Verifica se os parâmetros de conexão não estão vazios
        if db_host and db_name and db_user and db_pass:
            # Conecta ao banco de dados
            conn = connect_to_database(db_host, db_port, db_name, db_user, db_pass)
        else:
            st.warning("Por favor, preencha todos os parâmetros de conexão.")

    # Cria um formulário para envolver os inputs e o botão de busca
    with st.form(key='search_form'):
        # Input de texto para o nome da tabela
        table_name = st.text_input("Nome da Tabela", key="table_name")

        # Botão para executar a consulta
        search_button = st.form_submit_button("Buscar Dados")

    # Verifica se o botão de busca foi pressionado
    if search_button:
        if table_name:
            conn = connect_to_database(db_host, db_port, db_name, db_user, db_pass)
            if conn:
                with st.spinner("Buscando dados..."):
                    # Busca os dados da tabela
                    df = fetch_table_data(conn, table_name)
                    if df is not None:
                        st.write("Dados da tabela:")
                        st.dataframe(df)
            else:
                st.warning("Por favor, conecte ao banco de dados antes de buscar os dados.")
        else:
            st.warning("Por favor, insira o nome da tabela.")

# Executa a função principal
_main()
