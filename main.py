import streamlit as st
from app.utils import redirect

def config():
    try:
        st.set_page_config(
            page_title="DataBlue",
            layout="wide",
            initial_sidebar_state="expanded",
            page_icon="assets/icon.png"
        )
        st.logo("assets/logo.png")

        stylesheet()

        if "username" not in st.session_state:
            redirect("auth")
        else:
            st.sidebar.write(st.session_state["name"])
            st.sidebar.write(st.session_state["workspace"] if "workspace" in st.session_state else "No workspace")
        
        menu()
    except Exception as error:
        print(error)    

def stylesheet():
    css = open("app/stylesheet.css")
    st.write(f"<style>{css.read()}</style>", unsafe_allow_html=True)

def menu():    
    st.sidebar.page_link("main.py", label="Main Page", icon="🏠")
    st.sidebar.page_link("pages/data_import.py", label="Imported Data", icon="📂")
    st.sidebar.page_link("pages/data_preparation.py", label="Data Preparation", icon="🧩")
    st.sidebar.page_link("pages/buckets.py", label="S3 Buckets", icon="🗄️")
    st.sidebar.page_link("pages/dbs.py", label="DBs Connections", icon="🗂️")
    st.sidebar.page_link("pages/chat_bot.py", label="ChatBot", icon="🤖")
    # st.sidebar.page_link("pages/chat_test.py", label="chatBot", icon="🤖")
    st.sidebar.button
    
    if st.sidebar.button("⚙️ Settings"):
        redirect("settings")
    if st.sidebar.button("🔒 Logout"):
        del st.session_state["username"]
        del st.session_state["workspace"]
        st.rerun()

if __name__ == "__main__":
    config()
    
    st.image("assets/logo_dark.png")

    row1 = st.columns(2)
    row2 = st.columns(2)
    with row1[0].container(border=True):
        st.image("assets/card_connect.png")
        st.subheader("Connect to your databases")
    with row1[1].container(border=True):
        st.image("assets/card_import.png")
        st.subheader("Import your data")
    with row2[0].container(border=True):
        st.image("assets/card_prepare.png")
        st.subheader("Begin preparations")
    with row2[1].container(border=True):
        st.image("assets/card_analyze.png")
        st.subheader("Explore and analyze")
