import requests
from dotenv import load_dotenv
import os

load_dotenv(verbose=True)

API_URL = "https://router.huggingface.co/hf-inference/models/Helsinki-NLP/opus-mt-en-de"
headers = {
    "Authorization": f"Bearer {os.environ['HF_TOKEN']}",
}

text = input("Enter English text to translate to German: ")

payload = {
    "inputs": text,
}

response = requests.post(API_URL, json=payload, headers=headers)
print(response.status_code)
print(response.json())