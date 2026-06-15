# 🏥 Automated Clinical Triage Multi-Agent Pipeline

An intelligent, multi-agent orchestration system designed to automate clinical triage, validate symptom severity, and route patient data to the appropriate medical personnel using an LLM-powered rules engine.

## 🏗️ Architecture Overview

This project decouples the user interface from the backend orchestration, allowing for a highly scalable, dynamic workflow. 

* **Frontend:** React Flow (Drag-and-drop node canvas for UI interaction)
* **Orchestration Engine:** n8n (Handles logic routing, API calls, and data mapping)
* **Reasoning Agent:** Google Gemini (Processes clinical notes and outputs structured JSON)
* **Database / Memory:** Google Sheets (Acts as a mock Electronic Health Record [EHR] to store and retrieve patient history)
* **Notification Engine:** Slack (Multi-channel routing for standard logs and emergency alerts)

## ✨ Key Features

1. **Dynamic Routing (Switch & If Logic):** Automatically directs workflows based on the type of agent triggered in the UI (e.g., API Lookup vs. Reasoning Agent).
2. **Contextual Medical Memory:** Queries previous patient encounters before making a triage decision, allowing the AI to determine if a condition has escalated.
3. **Safety Priority Override:** A hardcoded rules engine that bypasses AI assumptions if specific "danger words" (e.g., *crushing chest pain, stroke*) are detected, guaranteeing emergency routing.
4. **Automated Escalation:** * **Standard Path:** Logs routine symptoms to a standard dashboard channel.
   * **Critical Path:** Triggers a high-priority `@channel` alert in an emergency Slack channel.
5. **Strict JSON Enforcement:** Forces the LLM to output cleanly parsed JSON to prevent pipeline crashes during logic evaluation.

## 🚀 Setup Instructions

### 1. Prerequisites
* Node.js and npm installed
* An active n8n instance (Cloud or Local)
* A Google Cloud Project with the Google Sheets API enabled
* A Slack Workspace with Webhook access

### 2. Frontend Setup (React Flow)
Navigate to the frontend directory and install dependencies:
```bash
cd frontend
npm install
npm run dev

### 3. Backend Setup (n8n)
Open your n8n workspace.

Click Workflow -> Import from File.

Select the n8n_clinical_triage_workflow.json file included in this repository.

Update the following credentials inside the n8n nodes:

Google Sheets Node: Connect your Google account and select your specific EHR spreadsheet.

Slack Nodes: Paste your specific Slack Webhook URLs for both the Standard and Emergency channels.

Message a Model Node: Ensure your Gemini API credentials are connected.

Click Activate (or Execute) to set the Webhook to listening mode.

🧪 Testing the Pipeline (Demo Protocol)
To verify the system is working, launch the React canvas and run the following tests:

Test 1: Standard Routine Check

Input: Patient ID: PAT-001 | Symptoms: Mild dry cough for two days. No fever.

Expected Result: The system retrieves patient history, logs the new visit, calculates Severity: STANDARD, and sends a formatted summary to the routine Slack channel.

Test 2: Emergency Escalation (Safety Override)

Input: Patient ID: PAT-999 | Symptoms: Severe crushing chest pain radiating to left arm.

Expected Result: The system triggers the Safety Override rule, calculates Severity: CRITICAL, bypasses standard routing, and fires a red-alert @channel notification to the emergency Slack channel.
