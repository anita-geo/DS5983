import json
import json.tool
from langchain_huggingface import HuggingFaceEmbeddings
from rag_model import Rag
from langchain_ollama import ChatOllama
from ragas import SingleTurnSample, evaluate, EvaluationDataset
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_recall,
    context_precision,
)
import pandas as pd
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper


truth_dataset_path = "./truth_dataset/truthDataGeneral.json"
truth_dataset_res_path = "./truth_dataset/truthDataGeneralRes.json"


with open(truth_dataset_path, 'r') as file:
    truth_dataset = json.load(file)

embedding_model = 'sentence-transformers/all-mpnet-base-v2'
persist_directory = 'chroma_huggingv4'
model = 'llama3.2:3b'

graph = Rag(embedding_model, persist_directory).compileGraph()

for data in truth_dataset:
    query = data["query"]
    response = graph.invoke({"question": query})
    
    data["contexts"] = [context.page_content for context in response['context']]
    data["answer"] = response['answer']

with open(truth_dataset_res_path, 'w') as file:
    json.dump(truth_dataset, file, indent=4)

with open(truth_dataset_res_path, 'r') as file:
    truth_dataset = json.load(file)

llm = ChatOllama(model = model)
embeddings = HuggingFaceEmbeddings(model_name=embedding_model)

samples = []
for data in truth_dataset[:1]:
    sample = SingleTurnSample(
        user_input=data["user_input"],
        retrieved_contexts=data["retrieved_contexts"],
        response=data["response"],
        reference=data["reference"]
    )
    samples.append(sample)

eval_dataset = EvaluationDataset(samples=samples)

result = evaluate(
    dataset=eval_dataset,
    metrics=[
        context_precision,
        context_recall,
        faithfulness,
        answer_relevancy,
    ],
    llm=LangchainLLMWrapper(llm),
    embeddings=LangchainEmbeddingsWrapper(embedding_model)
)

df = result.to_pandas()
print(df)