from process_pdf import ProcessPdf
from rag_model import Rag
import os

if __name__ == '__main__':
    model = 'sentence-transformers/all-mpnet-base-v2'
    persist_directory = 'chroma_huggingv4'
    os.environ["LANGCHAIN_API_KEY"] = "api-key"
    os.environ["LANGCHAIN_TRACING_V2"] = "true"

    ProcessPdf(model, persist_directory).store_docs(True)

    graph = Rag(model, persist_directory).compileGraph()
    questions = [
    "Which faculty members are involved in AI for social good?",
    "Which professors have PhDs in computer science from Rutgers University?",
    "Who is Yun Raymond Fu, and what are his main research interests?",
    "Who has expertise in personal health informatics?",
    "Where did Paul Hand do his PhD?"
    ]

    for question in questions:
        response = graph.invoke({"question": question})
        print(f"Question: {question}")
        print(f"Answer: {response['answer']}\n")
