from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import requests
import json
import tempfile

app = FastAPI(title="AI Code Review Backend")

# Allow Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:8501"] for stricter setup
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Ollama Settings ---
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "codellama"  # Make sure you have pulled this model: `ollama pull codellama`


# ---------- Helper Functions ----------

def call_ollama(prompt: str):
    """
    Sends a text prompt to the local Ollama model and returns its response text.
    """
    payload = {"model": MODEL_NAME, "prompt": prompt, "stream": False}
    try:
        r = requests.post(OLLAMA_URL, json=payload, timeout=120)
        r.raise_for_status()
        data = r.json()
        # Ollama returns {"response": "..."} when stream=False
        return data.get("response", "").strip()
    except Exception as e:
        return f"[Error contacting LLM: {e}]"


def run_lint_check(code: str):
    """
    Optionally runs pylint and extracts key messages.
    """
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode="w") as tmp:
            tmp.write(code)
            tmp_path = tmp.name

        import subprocess
        result = subprocess.run(["pylint", tmp_path, "-rn", "--score", "n"],
                                capture_output=True, text=True)
        output = result.stdout
        issues = []
        for line in output.splitlines():
            if ":" in line and ("error" in line or "warning" in line):
                issues.append(line.strip())
        return issues[:5]  # limit to first 5
    except Exception:
        return []


# ---------- Routes ----------

@app.post("/review")
async def review_code(code: str = Form(...)):
    """
    Receives source code, performs static + AI review, and returns analysis.
    """
    # 1. Static Analysis
    lint_issues = run_lint_check(code)

    # 2. AI Review
    system_prompt = """You are an expert software reviewer.
Analyze the following code for potential issues, best practices, and improvements.
Return your response in JSON format with a list of findings:
[
  {
    "issue_type": "bug/style/optimization/security",
    "description": "what is wrong",
    "line_number": 10,
    "suggested_fix": "how to fix it"
  }
]
"""
    ai_feedback_raw = call_ollama(system_prompt + "\n\nCode:\n" + code)

    # Attempt to parse model response if it returns JSON
    try:
        ai_feedback = json.loads(ai_feedback_raw)
    except Exception:
        ai_feedback = [{"issue_type": "general", "description": ai_feedback_raw, "line_number": "-", "suggested_fix": ""}]

    return {"lint_issues": lint_issues, "ai_feedback": ai_feedback}
