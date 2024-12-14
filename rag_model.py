from langchain_core.documents import Document
from langchain_ollama import ChatOllama
from typing_extensions import List, TypedDict
from process_pdf import ProcessPdf
from langchain import hub
from langgraph.graph import START, StateGraph

prompt_template = """You are a helpful assistant named HuskyLlama. You specialize in answering questions about professors at Northeastern University. You are still learning, so use the provided context to answer questions accurately. 

Use the following pieces of retrieved context to answer the question concisely. If you don't know the answer based on the context, say "I don't know." Keep your answer to three sentences maximum. 

Question: {question}

Context: {context}

Answer:"""

class State(TypedDict):
    question: str
    context: List[Document]
    answer: str

class Rag:
    def __init__(self, embedding_model, persist_directory):
        self.model_name = 'llama3.2:3b'
        # self.prompt = hub.pull("rlm/rag-prompt")
        self.prompt = prompt_template
        self.embedding_model = embedding_model
        self.persist_directory = persist_directory
        self.llm = ChatOllama(model = self.model_name, temperature = 0.8, num_predict = 256)


    def retrieve(self, state: State):
        vector_store = ProcessPdf(self.embedding_model, self.persist_directory).vector_store()
        retrieved_docs = vector_store.similarity_search(state["question"])
        return {"context": retrieved_docs}

    def generate(self, state: State):
        docs_content = "\n\n".join(doc.page_content for doc in state["context"])
        # messages = self.prompt.invoke({"question": state["question"], "context": docs_content})
        messages = self.prompt.format(question=state["question"], context=state["context"])
        response = self.llm.invoke(messages)
        return {"answer": response.content}
    
    def compileGraph(self):
        graph_builder = StateGraph(State).add_sequence([self.retrieve, self.generate])
        graph_builder.add_edge(START, "retrieve")
        graph = graph_builder.compile()
        return graph