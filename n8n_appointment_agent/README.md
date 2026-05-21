# 🎙️ AI Voice Appointment Booking Agent

A multimodal AI assistant that allows users to seamlessly book, cancel, and manage Google Calendar appointments using natural voice commands or text input. 

Developed as part of the Datadrive internship works by Nithish Ra.

## 🌟 Features
* **Voice & Text Interface:** Uses the Web Speech API for real-time voice recognition and speech synthesis, with a fallback text input option.
* **Natural Language Processing:** Powered by an LLM via n8n to interpret complex user requests (e.g., "Cancel my 3 PM today and book one for tomorrow morning").
* **Live Google Calendar Integration:** Directly interacts with Google Calendar via OAuth 2.0 to check availability, create, update, and delete events.
* **Modern UI:** Features a responsive, light-theme glassmorphism dashboard with smooth animations and dynamic status indicators.
* **Fully Cloud-Hosted:** Backend engine runs 24/7 on the cloud, decoupled from the static frontend.

## 🏗️ Architecture

This project uses a decoupled Frontend/Backend architecture:

* **Frontend:** Pure HTML, CSS (Glassmorphism UI), and Vanilla JavaScript. Hosted statically on **GitHub Pages**.
* **Backend:** **n8n** (Node-based automation engine) running a custom workflow. Hosted on **Railway.app** with a PostgreSQL database.
* **Database/Storage:** Google Calendar API.

## 🚀 Deployment & Setup Instructions

### 1. Backend Setup (n8n on Railway)
1. Deploy an n8n instance using the [Railway n8n template](https://railway.app/new/template/n8n).
2. Generate a public Railway domain for your server.
3. Import the agent workflow (`.json` file) into your n8n workspace.
4. Set up a Google Cloud Project, enable the Google Calendar API, and create an OAuth 2.0 Client ID. 
5. Add your Railway n8n OAuth callback URL to your Google Cloud authorized redirect URIs.
6. Authenticate the Google Calendar nodes inside n8n.
7. Ensure the Webhook node is set to **Production** and copy the URL.

### 2. Frontend Setup (GitHub Pages)
1. Open the `index.html` file.
2. Locate the JavaScript `fetch` call inside the `processRequest` function.
3. Replace the placeholder URL with your live Railway Production Webhook URL:
   ```javascript
   const response = await fetch('https://[YOUR-RAILWAY-URL]/webhook/voice-booking', {
       method: 'POST',
       // ...
