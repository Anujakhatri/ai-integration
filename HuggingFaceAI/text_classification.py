from dotenv import load_dotenv
import os
import requests


load_dotenv(verbose=True)
API_URL = "https://router.huggingface.co/hf-inference/models/facebook/bart-large-mnli"
headers = {
    "Authorization": f"Bearer {os.environ['HF_TOKEN']}",
}
text=input("Enter the text to be classified:")

candidate_labels=["Technology","Education", "Sports", "Entertainment"]
payload = {
    "inputs": text,
    "parameters":{"candidate_labels": candidate_labels},
}
response = requests.post(API_URL, json=payload, headers=headers)
print(response.status_code)
print(response.json())


