import streamlit as st
from utility import create_tenant, check_naming

st.set_page_config(layout="centered")

with st.form("create_collection", clear_on_submit=True):
    collection_name = st.text_input(label="Collection name", value=None, max_chars=64)
    add_button = st.form_submit_button(
        label="Create", type="primary"
    )
    if add_button:
        if not check_naming(collection_name) or not len(collection_name):
            st.error("Tenant name should only contain alphanumeric characters (a-z, A-Z, 0-9), underscore (_), and hyphen (-), with a length between 1 and 64 characters'}")
        else:
            with st.spinner(text="Adding new collection"):
                create_tenant(collection_name)
            st.success(f"Succesfully added {collection_name}.")
