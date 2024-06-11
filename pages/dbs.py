from main import config
import pandas as pd
import streamlit as st
from urllib.parse import urlparse
import mysql.connector
from app.db_utils import connect_to_database, fetch_registered_connections, get_registered_connections

config()

# Define a função principal
def _main():
    st.title("Gerenciador de Conexões de Banco de Dados")

    # Função para editar uma conexão
    def edit_connection(conn, id, nome, string_conexao):
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE db_conexoes SET nome = %s, string_conexao = %s WHERE id = %s", (nome, string_conexao, int(id)))
            conn.commit()
            st.success("Conexão atualizada com sucesso!")
            st.experimental_rerun()
        except mysql.connector.Error as e:
            st.error(f"Erro ao atualizar a conexão: {e}")
        finally:
            cursor.close()

    # Função para remover uma conexão
    def remove_connection(conn, id):
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM db_conexoes WHERE id = %s", (int(id),))  # Convertendo para int
            conn.commit()
            st.success("Conexão removida com sucesso!")
            st.experimental_rerun()
        except mysql.connector.Error as e:
            st.error(f"Erro ao remover a conexão: {e}")
        finally:
            cursor.close()

    # Função para cadastrar uma nova conexão
    def add_connection(conn, nome, string_conexao):
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO db_conexoes (nome, string_conexao) VALUES (%s, %s)", (nome, string_conexao))
            conn.commit()
            st.success("Nova conexão cadastrada com sucesso!")
            st.experimental_rerun()
        except mysql.connector.Error as e:
            st.error(f"Erro ao cadastrar a conexão: {e}")
        finally:
            cursor.close()

    # Função para validar a string de conexão MySQL
    def validate_connection_string(connection_string):
        try:
            result = urlparse(connection_string)
            conn = mysql.connector.connect(
                host=result.hostname,
                port=result.port,
                database=result.path.lstrip('/'),
                user=result.username,
                password=result.password
            )
            conn.close()
            return True
        except mysql.connector.Error as e:
            st.error(f"Erro ao validar a string de conexão: {e}")
            return False

    # Função para buscar as tabelas de uma conexão MySQL
    def fetch_tables(conn):
        try:
            cursor = conn.cursor()
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            return [table[0] for table in tables]
        except mysql.connector.Error as e:
            st.error(f"Erro ao buscar tabelas: {e}")
            return []
        finally:
            cursor.close()

    # Função para buscar dados de uma tabela
    def fetch_table_data(conn, table_name):
        try:
            query = f"SELECT * FROM {table_name}"
            return pd.read_sql(query, conn)
        except mysql.connector.Error as e:
            st.error(f"Erro ao buscar dados da tabela: {e}")
            return pd.DataFrame()

    # Buscar conexões registradas
    db_host = "***REMOVED***"
    db_port = "***REMOVED***"
    db_name = "***REMOVED***"
    db_user = "***REMOVED***"
    db_pass = "***REMOVED***"

    main_conn = connect_to_database(db_host, db_port, db_name, db_user, db_pass)
    if main_conn:
        registered_connections = fetch_registered_connections(main_conn)
        if registered_connections:
            df_registered_connections = pd.DataFrame(registered_connections, columns=["ID", "Nome", "String de Conexão"])

            # Exibir a tabela de conexões registradas
            st.write("Conexões Registradas:")
            st.table(df_registered_connections[['Nome', 'String de Conexão']])

            # Selecionar conexão para edição/remoção
            selected_connection = st.selectbox("Selecione uma conexão para baixar dados, editar ou remover a conexão:", [""] + df_registered_connections["Nome"].tolist())

            if selected_connection:
                selected_data = df_registered_connections[df_registered_connections["Nome"] == selected_connection].iloc[0]
                nome_input = st.text_input("Nome da conexão", value=selected_data["Nome"], key="edit_nome")
                string_conexao_input = st.text_input("String de Conexão", value=selected_data["String de Conexão"], key="edit_string")

                if st.button("Salvar", key="save"):
                    edit_connection(main_conn, selected_data["ID"], nome_input, string_conexao_input)

                if st.button("Remover", key="remove"):
                    remove_connection(main_conn, selected_data["ID"])

                # Mostrar tabelas da conexão selecionada
                conn_string = selected_data["String de Conexão"]
                result = urlparse(conn_string)
                conn = mysql.connector.connect(
                    host=result.hostname,
                    port=result.port,
                    database=result.path.lstrip('/'),
                    user=result.username,
                    password=result.password
                )
                tables = fetch_tables(conn)

                selected_table = st.selectbox("Selecione uma tabela para visualizar:", [""] + tables)

                if selected_table:
                    table_data = fetch_table_data(conn, selected_table)
                    st.write(f"Dados da Tabela: {selected_table}")
                    st.dataframe(table_data)

                    # Botão para exportar a tabela para CSV
                    csv = table_data.to_csv(index=False)
                    st.download_button(
                        label="Exportar para CSV",
                        data=csv,
                        file_name=f"{selected_table}.csv",
                        mime="text/csv"
                    )

    # Inputs para cadastrar uma nova conexão
    st.write("Cadastrar Nova Conexão:")
    nome_novo_input = st.text_input("Nome da Nova Conexão", value="", key="novo_nome")
    string_conexao_novo_input = st.text_input("String de Conexão da Nova Conexão", value="", key="novo_string")

    # Botão para cadastrar uma nova conexão
    if st.button("Cadastrar", key="cadastrar"):
        if nome_novo_input and string_conexao_novo_input:
            if validate_connection_string(string_conexao_novo_input):
                add_connection(main_conn, nome_novo_input, string_conexao_novo_input)
            else:
                st.error("String de conexão inválida. Verifique os detalhes e tente novamente.")
        else:
            st.warning("Por favor, preencha todos os campos.")

# Executa a função principal
_main()
