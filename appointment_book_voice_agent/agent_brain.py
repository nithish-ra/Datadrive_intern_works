import os
import json
from groq import Groq
from datetime import datetime
import calendar_tools

# --- SET YOUR API KEY ---
os.environ["GROQ_API_KEY"] = "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"

client = Groq()
MODEL = 'llama-3.1-8b-instant'  # Free tier: 500K TPD (vs 100K for 70b)


def get_current_time_context():
    """Tells the LLM what time it is right now so it can calculate relative dates."""
    now = datetime.now()
    return (
        f"Today is {now.strftime('%A, %B %d, %Y')}. "
        f"The current time is {now.strftime('%I:%M %p')} IST (UTC+05:30)."
    )


# --- TOOL DEFINITIONS ---
tools = [
    {
        "type": "function",
        "function": {
            "name": "check_availability",
            "description": "Check if the calendar is free between a start and end time.",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_time_iso": {
                        "type": "string",
                        "description": "Start time in ISO 8601 format with IST offset (e.g. '2026-05-21T14:00:00+05:30')"
                    },
                    "end_time_iso": {
                        "type": "string",
                        "description": "End time in ISO 8601 format with IST offset"
                    }
                },
                "required": ["start_time_iso", "end_time_iso"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "book_appointment",
            "description": (
                "Book an appointment. end_time_iso is auto-computed from start_time_iso + duration_minutes "
                "so you NEVER need to pass end_time_iso. Automatically prevents double-booking and adds to "
                "waitlist if the slot is taken."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "start_time_iso": {
                        "type": "string",
                        "description": "Start time in ISO 8601 format with IST offset (e.g. '2026-05-22T10:00:00+05:30')"
                    },
                    "patient_name": {
                        "type": "string",
                        "description": "Full name of the person booking the appointment"
                    },
                    "phone_number": {
                        "type": "string",
                        "description": "Phone number of the person booking (must ask user if not provided)"
                    },
                    "duration_minutes": {
                        "type": "integer",
                        "description": "Duration of the appointment in minutes (default 60)"
                    }
                },
                "required": ["start_time_iso", "patient_name", "phone_number"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "cancel_appointment",
            "description": "Cancel an existing appointment and notify the next person on the waitlist if any.",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_time_iso": {
                        "type": "string",
                        "description": "Start time of the appointment to cancel in ISO 8601 format"
                    },
                    "end_time_iso": {
                        "type": "string",
                        "description": "End time of the appointment to cancel in ISO 8601 format"
                    }
                },
                "required": ["start_time_iso", "end_time_iso"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_appointment",
            "description": "Reschedule (update/move) an existing appointment to a new time slot. Checks the new slot for conflicts first.",
            "parameters": {
                "type": "object",
                "properties": {
                    "old_start_time_iso": {
                        "type": "string",
                        "description": "Current start time of the appointment in ISO 8601 format"
                    },
                    "old_end_time_iso": {
                        "type": "string",
                        "description": "Current end time of the appointment in ISO 8601 format"
                    },
                    "new_start_time_iso": {
                        "type": "string",
                        "description": "New desired start time in ISO 8601 format"
                    },
                    "new_end_time_iso": {
                        "type": "string",
                        "description": "New desired end time in ISO 8601 format"
                    },
                    "duration_minutes": {
                        "type": "integer",
                        "description": "Duration in minutes (default 60)"
                    }
                },
                "required": ["old_start_time_iso", "old_end_time_iso", "new_start_time_iso", "new_end_time_iso"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_available_slots",
            "description": "Get all free appointment slots of a given duration on a specific date. Use this when the user asks 'what slots are available' or 'when can I book'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "date_iso": {
                        "type": "string",
                        "description": "The date to check in YYYY-MM-DD format (e.g. '2026-05-21')"
                    },
                    "slot_duration_minutes": {
                        "type": "integer",
                        "description": "Duration of each appointment slot in minutes (default 60)"
                    },
                    "work_start_hour": {
                        "type": "integer",
                        "description": "Start of working hours in 24h format (default 9)"
                    },
                    "work_end_hour": {
                        "type": "integer",
                        "description": "End of working hours in 24h format (default 18)"
                    }
                },
                "required": ["date_iso"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "view_waitlist",
            "description": "View who is on the waitlist for a specific time slot.",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_time_iso": {
                        "type": "string",
                        "description": "Start time of the slot in ISO 8601 format"
                    },
                    "end_time_iso": {
                        "type": "string",
                        "description": "End time of the slot in ISO 8601 format"
                    }
                },
                "required": ["start_time_iso", "end_time_iso"],
            },
        },
    },
]

def _book_appointment_wrapper(start_time_iso: str, patient_name: str, phone_number: str, duration_minutes: int = 60):
    """Auto-computes end_time_iso from start + duration, then calls the real book_appointment."""
    from datetime import datetime, timedelta
    start_dt = datetime.fromisoformat(start_time_iso)
    end_dt = start_dt + timedelta(minutes=duration_minutes)
    # Preserve the original timezone offset string
    if '+' in start_time_iso:
        tz_offset = start_time_iso[start_time_iso.rfind('+'):]
    elif start_time_iso.endswith('Z'):
        tz_offset = 'Z'
    else:
        tz_offset = '+05:30'  # Default IST
    end_time_iso = end_dt.strftime('%Y-%m-%dT%H:%M:%S') + tz_offset
    return calendar_tools.book_appointment(start_time_iso, end_time_iso, patient_name, phone_number, duration_minutes)


# Map tool names to actual Python functions
AVAILABLE_FUNCTIONS = {
    "check_availability": calendar_tools.check_availability,
    "book_appointment":   _book_appointment_wrapper,
    "cancel_appointment": calendar_tools.cancel_appointment,
    "update_appointment": calendar_tools.update_appointment,
    "get_available_slots": calendar_tools.get_available_slots,
    "view_waitlist":      calendar_tools.view_waitlist,
}

# Argument keys each function expects (for safe dispatch)
FUNCTION_ARG_KEYS = {
    "check_availability": ["start_time_iso", "end_time_iso"],
    "book_appointment":   ["start_time_iso", "patient_name", "phone_number", "duration_minutes"],
    "cancel_appointment": ["start_time_iso", "end_time_iso"],
    "update_appointment": ["old_start_time_iso", "old_end_time_iso", "new_start_time_iso", "new_end_time_iso", "duration_minutes"],
    "get_available_slots": ["date_iso", "slot_duration_minutes", "work_start_hour", "work_end_hour"],
    "view_waitlist":      ["start_time_iso", "end_time_iso"],
}

SYSTEM_PROMPT = """You are a helpful multilingual scheduling assistant. {time_context}

LANGUAGE:
- Detect the language the user is speaking (English, Tamil, Hindi, or others).
- Always respond in the SAME language the user used.
- Understand scheduling intent in all supported languages. Examples:
  • English: "Book an appointment for tomorrow at 3 PM"
  • Tamil: "நாளை மூன்று மணிக்கு appointment வேண்டும்"
  • Hindi: "कल तीन बजे appointment book करो"

TOOLS:
- check_availability: check if a slot is free.
- book_appointment: book a slot (auto-prevents double booking; adds to waitlist if busy).
  ⚠️ DO NOT pass end_time_iso — it is computed automatically from duration_minutes.
  Required args: start_time_iso, patient_name, phone_number. Optional: duration_minutes (default 60).
- cancel_appointment: cancel an existing booking (auto-notifies waitlist).
- update_appointment: reschedule an existing booking to a new time.
- get_available_slots: list all free slots on a given date — use when user asks "what's available" or "when can I book".
- view_waitlist: show who is waiting for a specific slot.

RULES:
- Always convert dates/times to ISO 8601 with IST offset: YYYY-MM-DDTHH:MM:SS+05:30
- Default appointment duration is 60 minutes unless the user specifies otherwise.
- ALWAYS ask for both name AND phone number before calling book_appointment if either is missing.
  Do not guess or use an empty phone number — ask the user first.
- Keep responses short, warm, and conversational — suitable for a voice call.
- If a slot is busy, offer to show available slots or add them to the waitlist.
"""


def run_conversation(user_prompt: str) -> str:
    """
    Full agentic loop:
      1. Send user message + tools to LLM
      2. Execute any tool calls
      3. Re-submit results to LLM for a final human-friendly reply
    Supports multi-step tool chaining (e.g. check then book).
    """
    print(f"\nUser: {user_prompt}")

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT.format(time_context=get_current_time_context()),
        },
        {
            "role": "user",
            "content": user_prompt,
        }
    ]

    # Agentic loop — keep going until no more tool calls
    for _ in range(5):  # Safety cap: max 5 rounds of tool use
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            max_tokens=4096
        )

        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        if not tool_calls:
            # No tools needed — return the text response
            final_text = response_message.content or ""
            print(f"Agent: {final_text}")
            return final_text

        # Append assistant's tool-call request to history
        messages.append(response_message)

        # Execute every requested tool
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = AVAILABLE_FUNCTIONS.get(function_name)

            if not function_to_call:
                tool_result = f"Error: unknown tool '{function_name}'"
            else:
                try:
                    raw_args = json.loads(tool_call.function.arguments)
                    # Only pass keys the function expects; omit unknowns
                    allowed_keys = FUNCTION_ARG_KEYS.get(function_name, [])
                    filtered_args = {k: v for k, v in raw_args.items() if k in allowed_keys}
                    print(f"🤖 Calling tool: {function_name} | args: {filtered_args}")
                    tool_result = str(function_to_call(**filtered_args))
                except Exception as e:
                    tool_result = f"Error executing {function_name}: {str(e)}"

            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": tool_result,
            })

    # Fallback if we somehow hit the cap
    final_response = client.chat.completions.create(model=MODEL, messages=messages)
    final_text = final_response.choices[0].message.content or ""
    print(f"Agent: {final_text}")
    return final_text


# --- TEST SUITE ---
if __name__ == "__main__":
    run_conversation("Hi, what can you help me with?")
    run_conversation("What slots are available tomorrow?")
    run_conversation("Can you check if 3 PM tomorrow is free?")

    # Tamil
    run_conversation("நாளை மூன்று மணிக்கு appointment வேண்டும். என் பெயர் Nithish, தொலைபேசி 9876543210.")

    # Hindi
    run_conversation("कल दोपहर 2 बजे की appointment book करो। मेरा नाम Rahul है, फोन 9123456789।")
