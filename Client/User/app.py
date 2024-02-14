import streamlit as st
from langchain_community.callbacks import StreamlitCallbackHandler
from langserve import RemoteRunnable

if "selected_collection" not in st.session_state:
    st.switch_page("pages/collections.py")


@st.cache_resource
def get_chain():
    return RemoteRunnable("http://server:8000/chain")


st.title(st.session_state["selected_collection"])

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "How can I help you?"}
    ]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    with st.chat_message("assistant") as msg:
        # st_callback = StreamlitCallbackHandler(msg)
        response = st.write_stream(
            get_chain().stream(
                {"tenant": st.session_state["selected_collection"], "prompt": prompt}
            )
        )
        st.session_state.messages.append(
            {"role": "assistant", "content": response}
        )
