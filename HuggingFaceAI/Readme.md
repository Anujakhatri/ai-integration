## 2. Hugging Face AI (HuggingFaceAI)

This folder contains separate Python scripts to demonstrate different Natural Language Processing (NLP) capabilities using the Hugging Face Inference API.

You can create a api from [hugging face](https://huggingface.co/settings/tokens)

### Available Scripts

- **`text_classification.py`**: Uses the `facebook/bart-large-mnli` model to classify input text into predefined categories (Technology, Education, Sports, Entertainment).
- **`text_summarization.py`**: Despite the name, this script currently uses `Helsinki-NLP/opus-mt-en-de` to **translate** English text into German.

### Setup Instructions

1. **Navigate to the directory**:
   ```bash
   cd HuggingFaceAI
   ```

2. **Create and activate a virtual environment** (optional but recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   The Hugging Face scripts rely on `requests` and `python-dotenv`.
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**:
   Create a `.env` file in the `HuggingFaceAI` directory and add your Hugging Face API token:
   ```env
   HF_TOKEN=your_hugging_face_token_here
   ```

5. **Run the Scripts**:
   ```bash
   python text_classification.py
   # OR
   python text_summarization.py
   ```
   Provide the required text inputs when prompted to see the model responses.

### Understanding the Model Base URL

In the Hugging Face scripts, you'll see an `API_URL` like this:
```python
API_URL = "https://router.huggingface.co/hf-inference/models/facebook/bart-large-mnli"
```
This is the URL for the **Hugging Face Serverless Inference API**, which allows you to call models directly without downloading them locally. 

**How to find the API URL for any model:**
1. Go to [Hugging Face Models](https://huggingface.co/models) and browse for a model that fits your use case (e.g., translation, text generation).
2. Click on the model to open its page (e.g., `facebook/bart-large-mnli`).
3. Click the **Deploy** button located in the top right area of the model page.
4. Select **Inference API (serverless)** from the dropdown menu.
5. You will see a code snippet that includes the exact `API_URL`. You can copy this URL and use it in your scripts. It typically follows the format: `https://router.huggingface.co/hf-inference/models/<organization>/<model-name>`.
