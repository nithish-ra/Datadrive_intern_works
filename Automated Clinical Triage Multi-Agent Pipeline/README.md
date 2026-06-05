# Automated Clinical Triage Multi-Agent Pipeline

## Overview
This project is an enterprise-grade, multi-agent AI architecture built in n8n. It automates the ingestion, evaluation, and routing of patient medical requests via email. Utilizing a Sequential Agentic Pipeline combined with Deterministic Routing and a Human-in-the-Loop (HITL) checkpoint, the system parses unstructured triage requests, sanitizes patient data, evaluates medical priority, and synthesizes professional clinical hand-off notes for medical staff.

## Author
**Nithish Ra** M.Tech (Integrated) Computer Science & Engineering | SSN College of Engineering

---

## System Architecture

The pipeline processes unstructured data into actionable medical alerts through five distinct phases:

1. **Asynchronous Ingestion (Trigger)**
   * Continuously monitors a connected Gmail inbox for incoming patient requests.
2. **Data Extraction (Agent 1)**
   * A Large Language Model (Google Gemini) parses the raw email text.
   * Maps unstructured data to a strict JSON schema (Name, Age, Symptoms, Duration).
3. **Validation & Triage (Agent 2)**
   * Evaluates the extracted JSON to assign a clinical priority (`CRITICAL` or `ROUTINE`).
   * Sanitizes personally identifiable information (PII) by obscuring the patient's last name.
   * Identifies missing critical data and flags the status as `REJECT`.
4. **Deterministic Routing (Logic Layer)**
   * Parses the validation status to route the workflow.
   * **False Path (Fallback):** Automatically emails the patient to request missing information.
   * **True Path (Synthesis):** Passes validated data to the final approval agent.
5. **Human-in-the-Loop (HITL) & Dispatch**
   * **Agent 3:** Synthesizes the validated data into a standardized, 3-bullet-point clinical hand-off note.
   * The draft is emailed to a reviewing Assistant Doctor with a unique webhook authorization link.
   * The workflow suspends execution in memory (`Wait` node) until the HTTP GET request is triggered.
   * Upon manual approval, the finalized note is dispatched to the Senior Attending Physician.

---

## Tech Stack & Tools

* **Orchestration:** n8n (Workflow Automation)
* **LLM Engine:** Google Gemini (models/gemini-3.1-flash-lite)
* **Integration:** Gmail API (OAuth2)
* **Data Handling:** JavaScript, JSON parsing, Prompt Engineering

---

## Installation & Setup

### 1. Import the Workflow
* Clone this repository.
* Open your n8n instance.
* Navigate to **Workflows** > **Import from File**.
* Upload the `n8n-Triage-Agent.json` file.

### 2. Configure Credentials
You will need to authenticate the following services within n8n:
* **Google Gemini (PaLM) API:** Generate an API key from Google AI Studio.
* **Gmail Account (OAuth2):** Connect the inbox that will act as the trigger and sender.

### 3. Environment Variables
Update the email addresses in the corresponding nodes to match your testing environment:
* **Send a message1 (Rejection Email):** Set to the simulated patient email.
* **Send a message2 (HITL Approval):** Set to the reviewing Assistant Doctor's email.
* **Send a message (Final Dispatch):** Set to the Senior Doctor's email.

---

## Testing Protocol

To execute a User Acceptance Testing (UAT) run:

1. Click **Execute Workflow** in n8n.
2. **Trigger:** Send an email from a patient account stating symptoms (e.g., "I have sharp stomach pains and a fever").
3. **Review:** Check the designated Assistant Doctor inbox. Review the AI-generated draft and click the `$execution.resumeUrl` embedded link.
4. **Verify:** Check the designated Senior Doctor inbox to confirm the receipt of the approved clinical hand-off note.

To test the edge-case/fallback logic, submit an email omitting symptoms and observe the automated rejection loop.

---

## License
This project is for educational and portfolio demonstration purposes.
