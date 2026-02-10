import os
import json
import csv
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

# Configuration
input_dir = "./data/1875"
output_file = "extracted_railway_results.csv"
model_id = "Qwen/Qwen2.5-7B-Instruct"

# Load Model and Tokenizer
print("Loading model...", flush=True)
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype="auto",
    device_map="auto"
)

# Initialize generation pipeline
pipe = pipeline("text-generation", model=model, tokenizer=tokenizer)

def extract_info(text):
    messages = [
        {"role": "system", "content": "You are an expert archival data extractor."},
        {"role": "user", "content": f"Extract the local 'Branch Name' (a city/town) and 'Total Members' from this 1875 OCR text. Ignore the Society name. Return ONLY JSON: {{\"branch\": \"string\", \"member_count\": \"string\"}}\n\nText: {text}"}
    ]
    try:
        outputs = pipe(messages, max_new_tokens=100, return_full_text=False, temperature=0.1)
        raw_response = outputs[0]['generated_text']
        start = raw_response.find('{')
        end = raw_response.rfind('}') + 1
        return json.loads(raw_response[start:end])
    except:
        return {"branch": "Error", "member_count": "Error"}

# Process Files
results = []
files = [f for f in os.listdir(input_dir) if f.endswith('.json')]

print(f"Starting processing for {len(files)} files...", flush=True)

for filename in files:
    with open(os.path.join(input_dir, filename), 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
            content = data.get('content', '')
            extracted = extract_info(content)
            results.append({
                "filename": filename,
                "branch": extracted.get("branch"),
                "member_count": extracted.get("member_count")
            })
            print(f"Processed: {filename}", flush=True)
        except Exception as e:
            print(f"Failed to read {filename}: {e}", flush=True)

# Save to CSV
with open(output_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=["filename", "branch", "member_count"])
    writer.writeheader()
    writer.writerows(results)

print(f"Extraction complete. Results saved to {output_file}", flush=True)
