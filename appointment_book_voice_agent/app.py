import gradio as gr
from faster_whisper import WhisperModel
import edge_tts
import os
import uuid
import sys
import asyncio

# Fix for Windows asyncio ProactorEventLoop conflict with edge_tts
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Import the agent brain
from agent_brain import run_conversation

# ─── TTS VOICE MAP ────────────────────────────────────────────────────────────
# edge-tts voice for each detected language (fallback: English)
TTS_VOICES = {
    "en": "en-US-AriaNeural",
    "ta": "ta-IN-PallaviNeural",   # Tamil
    "hi": "hi-IN-SwaraNeural",     # Hindi
}

# ─── LANGUAGE DETECTION (lightweight, no extra deps) ─────────────────────────
def detect_language(text: str) -> str:
    """
    Simple heuristic language detection.
    Returns 'ta' (Tamil), 'hi' (Hindi), or 'en' (English/default).
    """
    tamil_chars  = sum(1 for c in text if '\u0B80' <= c <= '\u0BFF')
    devanagari   = sum(1 for c in text if '\u0900' <= c <= '\u097F')
    if tamil_chars > 2:
        return "ta"
    if devanagari > 2:
        return "hi"
    return "en"

# ─── LOAD WHISPER ─────────────────────────────────────────────────────────────
print("Loading Whisper model (base, multilingual)...")
# 'base' is multilingual by default and handles Tamil, Hindi, English
whisper_model = WhisperModel("base", device="cpu", compute_type="int8")

# ─── TTS HELPER ───────────────────────────────────────────────────────────────
async def generate_audio(text: str, lang: str, output_path: str):
    """Converts text to speech using the language-appropriate voice."""
    voice = TTS_VOICES.get(lang, TTS_VOICES["en"])
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)

# ─── MAIN HANDLER ─────────────────────────────────────────────────────────────
async def process_voice_interaction(audio_filepath):
    """Full loop: Transcribe → Agent Brain → Speak"""
    if not audio_filepath:
        return "No audio detected. Please record your voice.", None

    # 1. Transcribe (Whisper auto-detects language)
    print("\n🎧 Transcribing audio...")
    segments, info = whisper_model.transcribe(audio_filepath, beam_size=5)
    user_text = "".join([seg.text for seg in segments]).strip()
    print(f"Transcribed ({info.language}): {user_text}")

    if not user_text:
        return "Could not understand the audio. Please try again.", None

    # 2. Send to agent
    print("🧠 Sending to Agent Brain...")
    agent_response_text = run_conversation(user_text)

    # 3. Detect language of the RESPONSE for correct TTS voice
    lang = detect_language(agent_response_text)

    # 4. Generate audio response
    print(f"🗣️ Generating audio response (lang={lang})...")
    unique_id = uuid.uuid4().hex
    output_audio_path = f"reply_{unique_id}.mp3"
    await generate_audio(agent_response_text, lang, output_audio_path)

    return agent_response_text, output_audio_path

# ─── TEXT-ONLY HANDLER (for users who prefer typing) ─────────────────────────
async def process_text_interaction(user_text: str):
    """Handles text input directly (no microphone needed)."""
    if not user_text or not user_text.strip():
        return "Please enter a message.", None

    print("🧠 Sending text to Agent Brain...")
    agent_response_text = run_conversation(user_text)

    lang = detect_language(agent_response_text)
    unique_id = uuid.uuid4().hex
    output_audio_path = f"reply_{unique_id}.mp3"
    await generate_audio(agent_response_text, lang, output_audio_path)

    return agent_response_text, output_audio_path

# ─── GRADIO UI ────────────────────────────────────────────────────────────────
print("Setting up Gradio UI...")

with gr.Blocks(title="AI Voice Scheduling Agent") as demo:
    gr.Markdown("# 🎙️ AI Voice Scheduling Agent")
    gr.Markdown(
        "Supports **English 🇬🇧 · Tamil 🇮🇳 · Hindi 🇮🇳**\n\n"
        "Speak or type your request — the agent will check availability, "
        "book, cancel, reschedule, show free slots, and manage waitlists."
    )

    with gr.Tabs():
        # ── Voice Tab ──────────────────────────────────────────────────────────
        with gr.Tab("🎤 Voice"):
            with gr.Row():
                with gr.Column():
                    audio_input = gr.Audio(
                        sources=["microphone"],
                        type="filepath",
                        label="Your Voice (English / Tamil / Hindi)"
                    )
                    voice_submit_btn = gr.Button("Send to Agent", variant="primary")

                with gr.Column():
                    voice_text_output  = gr.Textbox(label="Agent's Reply (text)", lines=4)
                    voice_audio_output = gr.Audio(label="Agent's Voice Reply", autoplay=True)

            voice_submit_btn.click(
                fn=process_voice_interaction,
                inputs=[audio_input],
                outputs=[voice_text_output, voice_audio_output]
            )

        # ── Text Tab ───────────────────────────────────────────────────────────
        with gr.Tab("⌨️ Text"):
            with gr.Row():
                with gr.Column():
                    text_input = gr.Textbox(
                        placeholder=(
                            "Type in English, Tamil, or Hindi…\n"
                            "e.g. 'Book 3 PM tomorrow for Nithish'\n"
                            "நாளை மூன்று மணிக்கு appointment வேண்டும்\n"
                            "कल 3 बजे appointment book करो"
                        ),
                        lines=3,
                        label="Your Message"
                    )
                    text_submit_btn = gr.Button("Send", variant="primary")

                with gr.Column():
                    text_text_output  = gr.Textbox(label="Agent's Reply (text)", lines=4)
                    text_audio_output = gr.Audio(label="Agent's Voice Reply", autoplay=True)

            text_submit_btn.click(
                fn=process_text_interaction,
                inputs=[text_input],
                outputs=[text_text_output, text_audio_output]
            )

    gr.Markdown(
        "---\n"
        "**Example commands:**\n"
        "- *What slots are free tomorrow?*\n"
        "- *Book 10 AM on May 22nd for Priya, phone 9876543210*\n"
        "- *Cancel my 3 PM appointment today*\n"
        "- *Reschedule 2 PM today to 4 PM*\n"
        "- *நாளை காலை 10 மணிக்கு slot இருக்கா?*\n"
        "- *कल की 2 बजे की appointment cancel करो*"
    )

if __name__ == "__main__":
    demo.launch(theme=gr.themes.Soft())
