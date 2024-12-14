from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from process_pdf import ProcessPdf
from numpy import dot
from numpy.linalg import norm

def cosine_similarity(v1, v2):
    return dot(v1, v2) / (norm(v1) * norm(v2))

file_path = "pdf_people/Paul Hand.pdf"
loader = PyPDFLoader(file_path)

docs = loader.load()

print(len(docs))
print(f"{docs[0].page_content[:200]}\n")
print(docs[0].metadata)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=200, chunk_overlap=10, add_start_index=True
)
all_splits = text_splitter.split_documents(docs)

print(len(all_splits))

print(all_splits[0])
print("\n\n\n\n")
print(all_splits[1])
print("\n\n\n\n")
print(all_splits[2])
print("\n\n\n\n")

embeddings = OllamaEmbeddings(model="llama3.2:3b")

vector_1 = embeddings.embed_query(all_splits[0].page_content)
vector_2 = embeddings.embed_query(all_splits[1].page_content)

assert len(vector_1) == len(vector_2)
print(f"Generated vectors of length {len(vector_1)}\n")
print(vector_1[:10])

vector_store = Chroma(embedding_function=embeddings)

vector_1 = embeddings.embed_query(all_splits[0].page_content)
vector_2 = embeddings.embed_query(all_splits[1].page_content)
vector_3 = embeddings.embed_query(all_splits[2].page_content)

print(f"Cosine similarity between chunk 0 and 1: {cosine_similarity(vector_1, vector_2)}")
print(f"Cosine similarity between chunk 0 and 2: {cosine_similarity(vector_1, vector_3)}")


ids = vector_store.add_documents(documents=all_splits)
print("Document IDs added to the vector store:", ids)

results = vector_store.similarity_search(
    "Where did Prof. Paul Hand located?"
)
print("Where did Prof. Paul Hand located?\n")
print(results[0])
print("\n\n\n\n")
results = vector_store.similarity_search(
    "Where did Prof. Paul Hand do his education?"
)
print( "Where did Prof. Paul Hand do his education?\n")
print(results[0])
print("\n\n\n\n")
results = vector_store.similarity_search(
    "Where did Prof. Paul Hand do his phD?"
)
print( "Where did Prof. Paul Hand do his phD?\n")
print(results[0])
print("\n\n\n\n")
results = vector_store.similarity_search(
    "What is Prof paul Hand working as?"
)
print("\n\n\n\n")
print("What is Prof paul Hand working as?\n")
print(results[0])


from langchain_huggingface import HuggingFaceEmbeddings
import os

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
docs = []
files = [file for file in os.listdir("pdf_people") if file.endswith('.pdf')]
for file in files:
    try:
        file_path = f"pdf_people/{file}"
        loader = PyPDFLoader(file_path)
        docs.extend(loader.load())
    except:
        print("eror")
text_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=30, add_start_index=True)
all_splits = text_splitter.split_documents(docs)

vector_store = Chroma(embedding_function=embeddings)
ids = vector_store.add_documents(documents=all_splits)

for idx, query in enumerate([
    "Where did Prof. Paul Hand locate?",
    "Where did Prof. Paul Hand do his education?",
    "Where did Prof. Paul Hand do his PhD?",
    "What is Prof. Paul Hand working as?"
]):
    results = vector_store.similarity_search(query)
    print(f"Query {idx}: {query}")
    print(f"Results: {results[0]}\n")