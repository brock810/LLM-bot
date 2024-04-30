from transformers import AutoTokenizer, LlamaForCausalLM
from human_eval.data import write_jsonl, read_problems
from tqdm import tqdm
import json

def read_problems_from_json(file_path):
    with open(file_path, 'r') as f:
        problems = json.load(f)
    return problems

def write_jsonl(file_path, data):
    with open(file_path, 'w') as f:
        for entry in data:
            f.write(json.dumps(entry) + '\n')
model_path = "Phind/Phind-CodeLlama-34B-v2"
model = LlamaForCausalLM.from_pretrained(model_path, device_map="auto")
tokenizer = AutoTokenizer.from_pretrained(model_path)

def generate_one_completion(prompt: str):
    tokenizer.pad_token = tokenizer.eos_token
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=4096)

    generate_ids = model.generate(inputs.input_ids.to("cuda"), max_new_tokens=384, do_sample=True, top_p=0.75, top_k=40, temperature=0.1)
    completion = tokenizer.batch_decode(generate_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]
    completion = completion.replace(prompt, "").split("\n\n\n")[0]

    return completion

def perform_human_eval(output_file="samples.jsonl", num_samples_per_task=1):
    problems = read_problems()
    samples = []

    for task_id in tqdm(problems):
        prompt = problems[task_id]["prompt"]
        for _ in range(num_samples_per_task):
            completion = generate_one_completion(prompt)
            samples.append({"task_id": task_id, "completion": completion})

    write_jsonl(output_file, samples)

if __name__ == "__main__":
    perform_human_eval(output_file="samples.jsonl", num_samples_per_task=1)
