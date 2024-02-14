import streamlit as st
import requests

GRID_COL_NUM = 3

st.set_page_config(layout="wide")
st.title("Select collection")

with st.spinner(text="Getting collections"):
    tenants = requests.get("http://server:8000/tenants").json()
# tenants


def select_collection(collection_name):
    st.session_state["selected_collection"] = collection_name


grid = st.columns(GRID_COL_NUM, gap="medium")
for i, name in enumerate(tenants):
    with grid[i % GRID_COL_NUM]:
        if st.button(
            label=name,
            on_click=select_collection,
            args=[name],
            use_container_width=True,
        ):
            st.switch_page("app.py")
