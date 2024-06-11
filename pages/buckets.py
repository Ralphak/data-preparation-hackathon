from main import config
import streamlit as st
import pandas as pd
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from app.db_utils import fetch_registered_s3_connections, save_s3_connection, delete_s3_connection, connect_to_database

# Inicializa a variável de estado para recarregamento da página
if 'reload_page' not in st.session_state:
    st.session_state.reload_page = False

config()

# Função para carregar as conexões existentes
def load_connections():
    connections = fetch_registered_s3_connections(conn)
    st.session_state.s3_connections = pd.DataFrame(connections, columns=['id', 'name', 'aws_access_key_id', 'aws_secret_access_key', 'region'])

# Função para adicionar uma nova conexão
def add_connection(name, aws_access_key_id, aws_secret_access_key, region):
    if save_s3_connection(conn, name, aws_access_key_id, aws_secret_access_key, region):
        st.success("Conexão adicionada com sucesso!")
        load_connections()
        st.session_state.reload_page = True
    else:
        st.error("Falha ao adicionar conexão.")

# Função para deletar uma conexão existente
def delete_connection(id):
    if delete_s3_connection(conn, id):
        st.success("Conexão deletada com sucesso!")
        load_connections()
        st.session_state.reload_page = True
    else:
        st.error("Falha ao deletar conexão.")

# Função para testar uma conexão ao S3
def test_connection(aws_access_key_id, aws_secret_access_key, region):
    try:
        s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=region)
        s3.list_buckets()
        return True
    except (NoCredentialsError, PartialCredentialsError):
        return False

# Função para listar os buckets no S3
def list_buckets(s3_client):
    response = s3_client.list_buckets()
    return [bucket['Name'] for bucket in response['Buckets']]

# Função para listar os objetos em um bucket
def list_objects(s3_client, bucket_name, prefix=''):
    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix, Delimiter='/')
    folders = response.get('CommonPrefixes', [])
    files = response.get('Contents', [])
    return folders, files

# Função para gerar um link de download direto para um arquivo no S3
def generate_download_url(s3_client, bucket_name, object_name):
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name, 'Key': object_name})
    except Exception as e:
        st.error(f"Erro ao gerar URL: {str(e)}")
        return None
    return response


# Configurações do banco de dados
db_host = "***REMOVED***"
db_port = "***REMOVED***"
db_name = "***REMOVED***"
db_user = "***REMOVED***"
db_pass = "***REMOVED***"

# Estabelecendo conexão com o banco de dados
conn = connect_to_database(db_host, db_port, db_name, db_user, db_pass)

# Função principal
def main():
    if st.session_state.reload_page:
        st.session_state.reload_page = False
        st.experimental_rerun()

    load_connections()

    st.title("Gerenciador de Conexões ao S3 da Amazon")

    st.subheader("Conexões Existentes")
    st.dataframe(st.session_state.s3_connections)

    st.subheader("Adicionar / Deletar Conexão")

    operation = st.selectbox("Operação", ["Adicionar", "Deletar"])

    if operation == "Adicionar":
        if 'name' not in st.session_state:
            st.session_state.name = ""
        if 'aws_access_key_id' not in st.session_state:
            st.session_state.aws_access_key_id = ""
        if 'aws_secret_access_key' not in st.session_state:
            st.session_state.aws_secret_access_key = ""
        if 'region' not in st.session_state:
            st.session_state.region = ""

        name = st.text_input("Nome da Conexão", st.session_state.name)
        st.session_state.name = name

        aws_access_key_id = st.text_input("AWS Access Key ID", st.session_state.aws_access_key_id)
        st.session_state.aws_access_key_id = aws_access_key_id

        aws_secret_access_key = st.text_input("AWS Secret Access Key", st.session_state.aws_secret_access_key, type="password")
        st.session_state.aws_secret_access_key = aws_secret_access_key

        region = st.selectbox("Região", ["us-east-1", "us-west-1", "us-west-2", "eu-west-1", "eu-central-1", "ap-southeast-1", "ap-northeast-1", "sa-east-1"], index=0)
        st.session_state.region = region

    if operation == "Deletar":
        connection_id = st.selectbox("Selecionar Conexão para Deletar", st.session_state.s3_connections['id'])

    submit_button = st.button('Executar')

    if submit_button:
        if operation == "Adicionar":
            if test_connection(st.session_state.aws_access_key_id, st.session_state.aws_secret_access_key, st.session_state.region):
                add_connection(st.session_state.name, st.session_state.aws_access_key_id, st.session_state.aws_secret_access_key, st.session_state.region)
            else:
                st.error("Falha ao adicionar conexão: Credenciais ou região inválidas.")
        elif operation == "Deletar":
            delete_connection(connection_id)

        st.experimental_rerun()

    st.subheader("Listar Buckets")
    selected_connection = st.selectbox("Selecionar Conexão", st.session_state.s3_connections['name'])

    if st.button('Listar Buckets'):
        selected_connection_details = st.session_state.s3_connections[st.session_state.s3_connections['name'] == selected_connection].iloc[0]
        s3_client = boto3.client(
            's3',
            aws_access_key_id=selected_connection_details['aws_access_key_id'],
            aws_secret_access_key=selected_connection_details['aws_secret_access_key'],
            region_name=selected_connection_details['region']
        )
        buckets = list_buckets(s3_client)
        st.session_state.buckets = buckets

    if 'buckets' in st.session_state:
        st.write("Buckets:")
        selected_bucket = st.selectbox("Selecionar Bucket", st.session_state.buckets)

        if st.button('Listar Pastas no Bucket'):
            selected_connection_details = st.session_state.s3_connections[st.session_state.s3_connections['name'] == selected_connection].iloc[0]
            s3_client = boto3.client(
                's3',
                aws_access_key_id=selected_connection_details['aws_access_key_id'],
                aws_secret_access_key=selected_connection_details['aws_secret_access_key'],
                region_name=selected_connection_details['region']
            )
            folders, _ = list_objects(s3_client, selected_bucket)
            folder_names = [folder['Prefix'] for folder in folders]
            st.session_state.folders = folder_names

    if 'folders' in st.session_state:
        st.write("Pastas:")
        selected_folder = st.selectbox("Selecionar Pasta", st.session_state.folders)
        
        if st.button('Listar Arquivos na Pasta'):
            selected_connection_details = st.session_state.s3_connections[st.session_state.s3_connections['name'] == selected_connection].iloc[0]
            s3_client = boto3.client(
                's3',
                aws_access_key_id=selected_connection_details['aws_access_key_id'],
                aws_secret_access_key=selected_connection_details['aws_secret_access_key'],
                region_name=selected_connection_details['region']
            )
            _, files = list_objects(s3_client, selected_bucket, selected_folder)
            file_names = [file['Key'] for file in files]
            if file_names:
                st.write("Arquivos:")
                for file in file_names:
                    download_url = generate_download_url(s3_client, selected_bucket, file)
                    if download_url:
                        st.markdown(f"[{file}]({download_url})")
                    else:
                        st.write(file)

            else:
                st.write("Nenhum arquivo encontrado na pasta.")

if __name__ == "__main__":
    main()
