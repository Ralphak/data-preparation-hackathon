import mysql.connector
import pandas as pd

def connect_to_database(db_host, db_port, db_name, db_user, db_pass):
    try:
        conn = mysql.connector.connect(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_pass
        )
        return conn
    except mysql.connector.Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

def fetch_registered_connections(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, string_conexao FROM db_conexoes")
        data = cursor.fetchall()
        return data
    except mysql.connector.Error as e:
        print(f"Erro ao buscar conexões registradas: {e}")
        return []
    finally:
        cursor.close()

# pega todas as linhas da tabela s3_conexoes
def fetch_registered_s3_connections(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, aws_access_key_id, aws_secret_access_key, region FROM s3_conexoes")
        data = cursor.fetchall()
        return data
    except mysql.connector.Error as e:
        print(f"Erro ao buscar conexões registradas: {e}")
        return []
    finally:
        cursor.close()

# salva uma nova conexão no banco de dados
def save_s3_connection(conn, name, aws_access_key_id, aws_secret_access_key, region):
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO s3_conexoes (name, aws_access_key_id, aws_secret_access_key, region) VALUES (%s, %s, %s, %s)", (name, aws_access_key_id, aws_secret_access_key, region))
        conn.commit()
        return True
    except mysql.connector.Error as e:
        print(f"Erro ao salvar conexão: {e}")
        return False
    finally:
        cursor.close()

# atualiza os dados de uma conexão no banco de dados
def update_s3_connection(conn, id, name, aws_access_key_id, aws_secret_access_key, region):
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE s3_conexoes SET name=%s, aws_access_key_id=%s, aws_secret_access_key=%s, region=%s WHERE id=%s", (name, aws_access_key_id, aws_secret_access_key, region, id))
        conn.commit()
        return True
    except mysql.connector.Error as e:
        print(f"Erro ao atualizar conexão: {e}")
        return False
    finally:
        cursor.close()


# deleta uma conexão do banco de dados
def delete_s3_connection(conn, id):
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM s3_conexoes WHERE id=%s", (id,))
        conn.commit()
        return True
    except mysql.connector.Error as e:
        print(f"Erro ao deletar conexão: {e}")
        return False
    finally:
        cursor.close()

def get_registered_connections(db_host, db_port, db_name, db_user, db_pass):
    conn = connect_to_database(db_host, db_port, db_name, db_user, db_pass)
    if conn:
        connections = fetch_registered_connections(conn)
        conn.close()
        df_registered_connections = pd.DataFrame(connections, columns=["ID", "Nome", "String de Conexão"])
        return df_registered_connections
    else:
        return pd.DataFrame(columns=["ID", "Nome", "String de Conexão"])


# Example usage within the same file (this can be removed in production)
db_host = "***REMOVED***"
db_port = "***REMOVED***"
db_name = "***REMOVED***"
db_user = "***REMOVED***"
db_pass = "***REMOVED***"

df_connections = get_registered_connections(db_host, db_port, db_name, db_user, db_pass)
print(df_connections)
