# 🤖 AI Voice Agent - Appointment Booking Frontend

A sleek, responsive React application built with Vite that serves as the frontend for an AI-powered voice booking agent. This app allows users to book, cancel, or update calendar appointments using natural language voice commands or text, and visualizes real-time Google Calendar availability in a dynamic 5-day grid.

## ✨ Features

*   **🎙️ Voice-to-Text & Text Input:** Users can hold the microphone button to speak their requests (using the native Web Speech API) or type them manually.
*   **🗣️ Text-to-Speech:** The AI assistant reads its responses aloud to create a seamless conversational experience.
*   **📅 Live 5-Day Availability Grid:** Displays a responsive, side-by-side calendar dashboard fetching real-time data from Google Calendar.
*   **🔄 Smart Pagination:** Easily navigate between previous and future weeks.
*   **⏳ Past-Date Filtering:** Automatically hides past dates based on the user's local system time to prevent accidental historical bookings.
*   **🎨 Premium UI/UX:** Features a modern glassmorphism design, interactive hover states, dynamic red/green slot statuses, and animated AI thinking/listening states.

## 🛠️ Tech Stack

*   **Framework:** [React](https://reactjs.org/) (via [Vite](https://vitejs.dev/))
*   **Styling:** Pure CSS (Flexbox/CSS Grid, Glassmorphism)
*   **Voice Integration:** Native Browser `SpeechRecognition` & `SpeechSynthesis` APIs
*   **Backend dependency:** Designed to connect to custom **n8n** webhook workflows (handling Gemini AI logic and Google Calendar API connections).

## 🚀 Getting Started

### Prerequisites
Make sure you have [Node.js](https://nodejs.org/) installed on your machine. You will also need your **n8n** backend workflows actively running to process the webhooks.

### 1. Installation
Clone the repository and navigate into the frontend folder:
```bash
cd ai-voice-agent_react
npm install
