# Parallel Patient Discharge Safety Checker

A healthcare pre-authorization assistant demonstrating a hierarchical/parallel multi-agent pattern using **Agno (Python)** and **n8n**.

## Architecture

- **n8n:** Acts as the trigger and routing logic (simulating a hospital EHR system).
- **Agno (FastAPI backend):** Runs three parallel AI agents evaluating drug interactions, logistics, and clinical vitals simultaneously.

## How to Run

### 1. Start the Python Backend

Navigate to the project folder, set up your environment, and start the server:

```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```
