import streamlit as st
from main import config
from app.db import create_tables, create_workspace, list_workspaces, remove_workspace
from app.utils import clear_session_cache

config()

# Inicializa o banco de dados
create_tables()

with st.expander("Manage Workspaces", expanded=True):
    # Seletor e botão de remoção de workspace
    st.subheader("Select and Remove Workspace")
    workspaces = list_workspaces(st.session_state['username']) if "username" in st.session_state else None
    col1, col2 = st.columns([3, 1])  # Define a proporção das colunas

    with col1:
        index = workspaces.index(st.session_state["workspace"]) if "workspace" in st.session_state else None
        selected_workspace = st.selectbox("Choose a workspace:", workspaces, index) if workspaces else None
        if selected_workspace and st.button("✔️ Choose"):
            st.write(f"You selected the workspace: {selected_workspace}")
            st.session_state["workspace"] = selected_workspace
            clear_session_cache()
            st.rerun()

    with col2:
        workspace_to_remove = st.selectbox("Choose a workspace to remove:", workspaces, placeholder="Choose an option", index=None) if workspaces else None
        if workspace_to_remove and st.button("❌ Remove", key="remove_button"):
            remove_workspace(st.session_state['username'], workspace_to_remove)
            st.success(f"Workspace '{workspace_to_remove}' removed successfully!")
            st.rerun()

    # Botão para criar workspace
    st.subheader("Create Workspace")
    workspace_name = st.text_input("New workspace name:")
    if st.button("➕ Create", key="create_button"):
        if not len(workspace_name):
            st.error("Workspace name is empty!")
        else:
            create_workspace(st.session_state['username'], workspace_name)
            st.success(f"Workspace '{workspace_name}' created successfully!")
            st.rerun()

    # Listar os workspaces existentes
    st.subheader("Existing workspaces")
    if workspaces:
        for ws in workspaces:
            st.write(f"- {ws}")
    else:
        st.write("You have no workspaces.")