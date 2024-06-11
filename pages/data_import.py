import streamlit as st
import pandas as pd
from main import config
from app.services import list_s3, upload_s3, get_s3_download_url, delete_s3
from app.utils import get_s3_filename, clear_session_cache

config()

st.title("Imported Data")

# File uploader
if "file_uploader_key" not in st.session_state:
    st.session_state["file_uploader_key"] = 0
uploaded_files = st.file_uploader(
    "Upload a file",
    type=["csv", "json"],
    key=st.session_state["file_uploader_key"],
    accept_multiple_files=True
)
if len(uploaded_files):
    with st.spinner("Uploading file..."):
        upload_s3(uploaded_files, "input")
    st.session_state["file_uploader_key"] += 1
    clear_session_cache()
    st.rerun()

# Data list
with st.spinner("Retrieving data..."):
    if "imported_data" not in st.session_state:
        list = list_s3("input")
        if list:
            list = pd.DataFrame(list)
            list = pd.DataFrame(
                data = {
                    "Name": list["Key"].apply(get_s3_filename),
                    "Last Modified": list["LastModified"],
                    "Size": list["Size"],
                    "Download": list["Key"].apply(get_s3_download_url)
                }
            )
            list["Remove"] = False
            st.session_state["imported_data"] = list
    
    if "imported_data" in st.session_state:
        checklist = st.data_editor(
            st.session_state["imported_data"],
            hide_index=True,
            disabled=["Name", "Last Modified", "Size", "Download"],
            column_config={
                "Download": st.column_config.LinkColumn(display_text="📄"),
                "Remove": st.column_config.CheckboxColumn(default=False)
            }
        )
        checked_files = checklist.loc[checklist["Remove"]]["Name"].tolist()
        if st.button("❌ Remove selected", disabled = not len(checked_files)):
            delete_s3(checked_files, "input")
            clear_session_cache()
            st.rerun()
    else:
        st.write("You have not imported any data")
