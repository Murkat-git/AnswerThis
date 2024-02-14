import weaviate
import streamlit as st
from utility import get_tenants


GRID_COL_NUM = 3

st.set_page_config(layout="wide")
st.title("Select collection")

with st.spinner(text="Getting collections"):
    tenants = sorted(get_tenants())
# tenants

# collections = client.collections.list_all(simple=True)
# collections = [collection for collection in collections if collection["description"]]
# collections = ["Calamity", "Stars above", "Thorium"]


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

with grid[(len(tenants)) % GRID_COL_NUM]:
    st.page_link(
        label="Create a new collection",
        icon="➕",
        page="pages/create_new_collection.py",
        use_container_width=True,
    )
