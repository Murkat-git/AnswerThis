import weaviate
import pandas as pd
import streamlit as st
from utility import get_db_client, process_file, get_all_chunks

if "selected_collection" not in st.session_state:
    st.switch_page("pages/collections.py")

st.title(st.session_state["selected_collection"])

client = get_db_client()

col1, col2 = st.columns(2)

with col2:
    with st.form("adding_data", clear_on_submit=True):
        uploaded_files = st.file_uploader(
            "Select files to add", accept_multiple_files=True
        )
        if st.form_submit_button(label="Load"):
            with st.spinner("Uploading files"):
                for uploaded_file in uploaded_files:
                    process_file(
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        st.session_state["selected_collection"],
                    )
            st.success("Files uploaded succesfully")

st.dataframe(
    pd.DataFrame.from_records(
        [
            vars(o)
            for o in get_all_chunks(st.session_state["selected_collection"]).objects
        ]
    )
)
