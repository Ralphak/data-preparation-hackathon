import streamlit as st
from main import stylesheet
from app.db import authenticate, add_user, create_tables, list_workspaces
from app.utils import redirect

stylesheet()

# Inicializa o banco de dados
create_tables()

# Função de login
def login():
    st.title("Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

    if submit:
        user = authenticate(username, password)
        if user:
            st.session_state["username"] = user[1]
            st.session_state["name"] = user[2]
            st.success(f"Welcome, {user[2]}!")
            st.rerun()
        else:
            st.error("Incorrect username or password.")

# Função de registro
def register():
    st.title("Register")

    username = st.text_input("New username")
    name = st.text_input("Full name")
    password = st.text_input("Password", type="password")
    if st.button("Register", key="register_button"):
        add_user(username, name, password)
        st.success("User registered successfully!")

# Função principal
def main():
    if "username" in st.session_state:
        workspaces = list_workspaces(st.session_state['username'])
        if workspaces:
            st.session_state["workspace"] = workspaces[0]
            redirect()
        else:
            redirect("settings")
    else:
        login_option = st.radio("Choose an option", ["🔑 Login", "📝 Register"])
        if login_option == "🔑 Login":
            login()
        else:
            register()

main()