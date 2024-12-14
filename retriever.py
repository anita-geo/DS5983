import streamlit as st
from langchain.callbacks.base import BaseCallbackHandler
from rag_model import Rag

st.set_page_config(page_title="LLM Chatbot with RAG", layout="wide")


class StreamlitCallbackHandler(BaseCallbackHandler):
    def __init__(self, container):
        self.container = container
        self.text = ""

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

model = 'sentence-transformers/all-mpnet-base-v2'
persist_directory = 'chroma_huggingv4'

graph = Rag(model, persist_directory).compileGraph()

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response_container = st.empty()
        with response_container:
            with st.spinner("Thinking..."):
                response = graph.invoke({"question": prompt})

        st.session_state.messages.append({"role": "assistant", "content": response['answer']})
        response_container.markdown(response['answer'])
