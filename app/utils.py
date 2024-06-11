import streamlit as st

def redirect(page="main"):
    page = "main.py" if page == "main" else f"pages/{page}.py"
    st.switch_page(page)

def get_s3_filename(key: str):
    return key.split("/").pop()

def get_file_extension(filename: str):
    return filename.split(".").pop().lower()

def clear_session_cache():
    keys = ["imported_data", "data_preparation"]
    for key in keys:
        if key in st.session_state: del st.session_state[key]