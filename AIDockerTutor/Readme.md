## 1. Google GenAI (AIDockerTutor)

This folder contains a console-based application (`app.py`) that interacts with the Gemini model. **Note:** While this might have been originally planned for OpenAI, it currently uses Google's `gemini-2.0-flash` model.

### Setup Instructions

1. **Navigate to the directory**:
   ```bash
   cd AIDockerTutor
   ```

2. **Create and activate a virtual environment** (optional but recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**:
   Create a `.env` file in the `AIDockerTutor` directory and add your Google Gemini API key:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

5. **Run the Application**:
   ```bash
   python app.py
   ```
   Follow the on-screen menu to ask questions to the AI.

### Getting Your Gemini API Key and Model Name

The script relies on the Google GenAI library and requires an API key to communicate with Google's models.

**How to get your API key:**
1. Go to [Google AI Studio](https://aistudio.google.com/).
2. Sign in with your Google account.
3. On the left sidebar, click on **Get API key**.
4. Click **Create API key** and copy it into your `.env` file as `GEMINI_API_KEY`.

**How to find different models:**
In `app.py`, you'll see the model specified like this:
```python
response = client.models.generate_content(
    model="gemini-2.0-flash",
    ...
)
```
If you want to use a different model (like `gemini-1.5-pro`), you can explore the available models on the [Gemini API Models documentation page](https://ai.google.dev/models/gemini). Simply replace `"gemini-2.0-flash"` in your script with your chosen model's name.

---