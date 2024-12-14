from rouge_score import rouge_scorer
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from rouge_score import rouge_scorer
import matplotlib.pyplot as plt
import json
import json.tool

def calculate_scores(generated_texts, reference_texts):
    assert len(generated_texts) == len(reference_texts)

    rouge_scorer_instance = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=True)
    smoothing_function = SmoothingFunction().method4

    results = []

    for gen, ref in zip(generated_texts, reference_texts):
        # Calculate ROUGE scores
        rouge_scores = rouge_scorer_instance.score(ref, gen)

        # Calculate BLEU score
        reference_tokens = [ref.split()]
        generated_tokens = gen.split()
        bleu_score = sentence_bleu(reference_tokens, generated_tokens, smoothing_function=smoothing_function)

        # Append results
        results.append({
            "generated": gen,
            "reference": ref,
            "rouge1": rouge_scores["rouge1"].fmeasure,
            "rouge2": rouge_scores["rouge2"].fmeasure,
            "rougeL": rouge_scores["rougeL"].fmeasure,
            "bleu": bleu_score
        })

    return results

def calculate_avg_score(scores):
    avg_rouge1 = 0
    avg_rouge2 = 0
    avg_rougeL = 0
    avg_bleu = 0

    for idx, score in enumerate(scores):
        print(f"Example {idx + 1}:")
        print(f"Generated: {score['generated']}")
        print(f"Reference: {score['reference']}")
        print(f"ROUGE-1: {score['rouge1']:.4f}")
        print(f"ROUGE-2: {score['rouge2']:.4f}")
        print(f"ROUGE-L: {score['rougeL']:.4f}")
        print(f"BLEU: {score['bleu']:.4f}\n")

        avg_rouge1 += score['rouge1']
        avg_rouge2 += score['rouge2']
        avg_rougeL += score['rougeL']
        avg_bleu += score['bleu']

    num_examples = len(scores)
    avg_scores = []
    avg_rouge1 /= num_examples
    avg_rouge2 /= num_examples
    avg_rougeL /= num_examples
    avg_bleu /= num_examples

    print("Averages:")
    print(f"Average ROUGE-1: {avg_rouge1:.4f}")
    print(f"Average ROUGE-2: {avg_rouge2:.4f}")
    print(f"Average ROUGE-L: {avg_rougeL:.4f}")
    print(f"Average BLEU: {avg_bleu:.4f}")

    avg_scores.append(avg_rouge1)
    avg_scores.append(avg_rouge2)
    avg_scores.append(avg_rougeL)
    avg_scores.append(avg_bleu)

    return avg_scores

truth_path_res_LLama = "./truth_dataset/truthDataProfessorLlama.json"
with open(truth_path_res_LLama, 'r') as file:
    truth_dataset = json.load(file)


reference_texts = []
generated_texts = []

for data in truth_dataset:
    reference_texts.append(data["reference"])
    generated_texts.append(data["answer"])
    
scores = calculate_scores(generated_texts, reference_texts)
avg_scores1 = calculate_avg_score(scores)

truth_path = "./truth_dataset/truthDataProfessforRag.json"
with open(truth_path, 'r') as file:
    truth_dataset = json.load(file)


reference_texts = []
generated_texts = []

for data in truth_dataset:
    reference_texts.append(data["reference"])
    generated_texts.append(data["response"])

scores = calculate_scores(generated_texts, reference_texts)
avg_scores2 = calculate_avg_score(scores)


metrics = ['ROUGE-1', 'ROUGE-2', 'ROUGE-L', 'BLEU']

bar_width = 0.25
x_indices = range(len(metrics))

plt.figure(figsize=(10, 6))
plt.bar([x - bar_width for x in x_indices], avg_scores1, width=bar_width, label='LLama3.2', color='#1877F2')
plt.bar([x for x in x_indices], avg_scores2, width=bar_width, label='RAG + LLama3.2', color='#8B0000')

plt.xticks(ticks=x_indices, labels=metrics)
plt.ylim(0, 1)
plt.title('Comparison of Average Metrics')
plt.ylabel('Score')
plt.xlabel('Metrics')
plt.legend()

plt.tight_layout()
plt.show()


truth_path = "./truth_dataset/truthDataGeneralRag.json"
with open(truth_path, 'r') as file:
    truth_dataset = json.load(file)


reference_texts = []
generated_texts = []

for data in truth_dataset:
    reference_texts.append(data["reference"])
    generated_texts.append(data["response"])

scores = calculate_scores(generated_texts, reference_texts)
avg_scores2 = calculate_avg_score(scores)

metrics = ['ROUGE-1', 'ROUGE-2', 'ROUGE-L', 'BLEU']

bar_width = 0.25
x_indices = range(len(metrics))

plt.figure(figsize=(10, 6))
plt.bar([x for x in x_indices], avg_scores2, width=bar_width, label='RAG + LLama3.2 for Across Professor data', color='black')

plt.xticks(ticks=x_indices, labels=metrics)
plt.ylim(0, 1)
plt.title('Comparison of Average Metrics')
plt.ylabel('Score')
plt.xlabel('Metrics')
plt.legend()

plt.tight_layout()
plt.show()