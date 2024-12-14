from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import os

class ProcessPdf:
    def __init__(self, model_name, persis_directory):
        self.folder_path = 'pdf_people'
        self.model_name = model_name
        self.docs = []
        self.persist_directory = persis_directory
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50, add_start_index=True)

    def load_doc(self):
        files = [file for file in os.listdir(self.folder_path) if file.endswith('.pdf')]
        for file in files:
            try:
                file_path = f"{self.folder_path}/{file}"
                loader = PyPDFLoader(file_path)

                professor_name = file.replace(".pdf", "")

                for doc in loader.load():
                    doc.metadata["professor_name"] = professor_name
                    self.docs.append(doc)
            except:
                print(f'There was an error reading file {file_path}')

    def split_text(self):
        if not self.docs:
            self.load_doc()
        return self.text_splitter.split_documents(self.docs)
    
    def vector_store(self):
        if self.model_name.startswith('llama'):
            embeddings = OllamaEmbeddings(model=self.model_name)
        else:
            embeddings = HuggingFaceEmbeddings(model_name=self.model_name)

        return Chroma(embedding_function=embeddings, persist_directory=self.persist_directory)

    def store_docs(self, printId: bool):
        vector_store = self.vector_store()
        all_splits = self.split_text()
        ids = vector_store.add_documents(documents=all_splits)

        if printId:
            print("Document IDs added to the vector store:", ids)
        
        print(f"Inserted {len(all_splits)} into the vector store.\n")