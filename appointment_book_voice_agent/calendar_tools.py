from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import json
import os

# --- CONFIGURATION ---
SERVICE_ACCOUNT_FILE = 'Key.json'
CALENDAR_ID = 'nithish2370014@ssn.edu.in'
SCOPES = ['https://www.googleapis.com/auth/calendar']
TIMEZONE = 'Asia/Kolkata'

# Waitlist stored as a JSON file (persists across runs)
WAITLIST_FILE = 'waitlist.json'

# Authenticate once
creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('calendar', 'v3', credentials=creds)


# ─── WAITLIST HELPERS ────────────────────────────────────────────────────────

def _load_waitlist() -> dict:
    if os.path.exists(WAITLIST_FILE):
        with open(WAITLIST_FILE, 'r') as f:
            return json.load(f)
    return {}

def _save_waitlist(waitlist: dict):
    with open(WAITLIST_FILE, 'w') as f:
        json.dump(waitlist, f, indent=2)

def _slot_key(start_iso: str, end_iso: str) -> str:
    return f"{start_iso}|{end_iso}"


# ─── CORE TOOL FUNCTIONS ─────────────────────────────────────────────────────

def check_availability(start_time_iso: str, end_time_iso: str) -> str:
    """
    Checks if the calendar is free between two specific times.
    Returns a clear AVAILABLE or BUSY result.
    """
    body = {
        "timeMin": start_time_iso,
        "timeMax": end_time_iso,
        "timeZone": TIMEZONE,
        "items": [{"id": CALENDAR_ID}]
    }

    print(f"Checking availability from {start_time_iso} to {end_time_iso}...")
    try:
        events_result = service.freebusy().query(body=body).execute()
        busy_slots = events_result.get('calendars', {}).get(CALENDAR_ID, {}).get('busy', [])
    except Exception as e:
        return f"Error checking availability: {str(e)}"

    if not busy_slots:
        return "Slot is AVAILABLE."
    else:
        busy_summary = "; ".join(
            f"{s['start']} to {s['end']}" for s in busy_slots
        )
        return f"Slot is BUSY. Conflicts: {busy_summary}"


def book_appointment(
    start_time_iso: str,
    end_time_iso: str,
    patient_name: str,
    phone_number: str,
    duration_minutes: int = 60
) -> str:
    """
    Books an appointment. Prevents double-booking by checking availability first.
    Adds to waitlist if the slot is taken. Supports custom duration.
    """
    # --- Recompute end time if a specific duration was given ---
    try:
        start_dt = datetime.fromisoformat(start_time_iso)
        end_dt = start_dt + timedelta(minutes=duration_minutes)
        # Preserve timezone offset
        if '+' in start_time_iso:
            tz_offset = start_time_iso[start_time_iso.rfind('+'):]
            end_time_iso = end_dt.strftime('%Y-%m-%dT%H:%M:%S') + tz_offset
        else:
            end_time_iso = end_dt.isoformat()
    except Exception:
        pass  # Fall back to the provided end_time_iso

    # --- Double-booking guard ---
    avail = check_availability(start_time_iso, end_time_iso)
    if "BUSY" in avail:
        # Add to waitlist
        waitlist = _load_waitlist()
        key = _slot_key(start_time_iso, end_time_iso)
        if key not in waitlist:
            waitlist[key] = []
        position = len(waitlist[key]) + 1
        waitlist[key].append({"name": patient_name, "phone": phone_number})
        _save_waitlist(waitlist)
        return (
            f"Sorry, that slot is already booked. "
            f"I've added {patient_name} to the waitlist at position #{position} "
            f"for {start_time_iso}. We will contact {phone_number} if a cancellation opens up."
        )

    # --- Book the event ---
    event = {
        'summary': f"Appointment: {patient_name}",
        'description': f"Automated booking.\nPhone: {phone_number}\nDuration: {duration_minutes} min",
        'start': {'dateTime': start_time_iso, 'timeZone': TIMEZONE},
        'end':   {'dateTime': end_time_iso,   'timeZone': TIMEZONE},
    }

    print(f"Booking appointment for {patient_name} ({duration_minutes} min)...")
    try:
        created = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
        return (
            f"Success! Appointment booked for {patient_name} "
            f"from {start_time_iso} to {end_time_iso} ({duration_minutes} min). "
            f"Event ID: {created.get('id', 'N/A')}"
        )
    except Exception as e:
        return f"Error booking appointment: {str(e)}"


def cancel_appointment(start_time_iso: str, end_time_iso: str) -> str:
    """
    Cancels an existing appointment in the given time window.
    Automatically notifies the first person on the waitlist (logs their details).
    """
    print(f"Searching for appointment between {start_time_iso} and {end_time_iso}...")
    try:
        events_result = service.events().list(
            calendarId=CALENDAR_ID,
            timeMin=start_time_iso,
            timeMax=end_time_iso,
            singleEvents=True
        ).execute()
        events = events_result.get('items', [])
    except Exception as e:
        return f"Error searching for appointments: {str(e)}"

    if not events:
        return "Error: No appointment found at that specific time to cancel."

    event_to_cancel = events[0]
    event_id = event_to_cancel['id']
    event_start = event_to_cancel['start'].get('dateTime', start_time_iso)
    event_end   = event_to_cancel['end'].get('dateTime', end_time_iso)

    try:
        service.events().delete(calendarId=CALENDAR_ID, eventId=event_id).execute()
    except Exception as e:
        return f"Error canceling appointment: {str(e)}"

    result = f"Success! Canceled: {event_to_cancel.get('summary', 'Unknown')}."

    # --- Check waitlist ---
    waitlist = _load_waitlist()
    key = _slot_key(event_start, event_end)
    if key in waitlist and waitlist[key]:
        next_person = waitlist[key].pop(0)
        if not waitlist[key]:
            del waitlist[key]
        _save_waitlist(waitlist)
        result += (
            f" Waitlist alert: {next_person['name']} ({next_person['phone']}) "
            f"is next in line — please contact them to confirm the slot."
        )
    else:
        result += " No one on the waitlist for this slot."

    return result


def update_appointment(
    old_start_time_iso: str,
    old_end_time_iso: str,
    new_start_time_iso: str,
    new_end_time_iso: str,
    duration_minutes: int = 60
) -> str:
    """
    Moves an existing appointment to a new time.
    Checks the new slot for conflicts before moving.
    """
    # Recompute new end time from duration if needed
    try:
        new_start_dt = datetime.fromisoformat(new_start_time_iso)
        new_end_dt = new_start_dt + timedelta(minutes=duration_minutes)
        if '+' in new_start_time_iso:
            tz_offset = new_start_time_iso[new_start_time_iso.rfind('+'):]
            new_end_time_iso = new_end_dt.strftime('%Y-%m-%dT%H:%M:%S') + tz_offset
        else:
            new_end_time_iso = new_end_dt.isoformat()
    except Exception:
        pass

    # Find the existing event
    print(f"Finding appointment to update between {old_start_time_iso} and {old_end_time_iso}...")
    try:
        events_result = service.events().list(
            calendarId=CALENDAR_ID,
            timeMin=old_start_time_iso,
            timeMax=old_end_time_iso,
            singleEvents=True
        ).execute()
        events = events_result.get('items', [])
    except Exception as e:
        return f"Error finding appointment: {str(e)}"

    if not events:
        return "Error: No appointment found at the old time slot."

    event_to_update = events[0]
    event_id = event_to_update['id']

    # Check new slot availability
    avail = check_availability(new_start_time_iso, new_end_time_iso)
    if "BUSY" in avail:
        return (
            f"Cannot reschedule — the new slot ({new_start_time_iso} to {new_end_time_iso}) "
            f"is already booked. Please choose another time."
        )

    # Update the event
    event_to_update['start'] = {'dateTime': new_start_time_iso, 'timeZone': TIMEZONE}
    event_to_update['end']   = {'dateTime': new_end_time_iso,   'timeZone': TIMEZONE}

    try:
        updated = service.events().update(
            calendarId=CALENDAR_ID,
            eventId=event_id,
            body=event_to_update
        ).execute()
        return (
            f"Success! Appointment '{updated.get('summary', '')}' rescheduled to "
            f"{new_start_time_iso} – {new_end_time_iso}."
        )
    except Exception as e:
        return f"Error updating appointment: {str(e)}"


def get_available_slots(
    date_iso: str,
    slot_duration_minutes: int = 60,
    work_start_hour: int = 9,
    work_end_hour: int = 18
) -> str:
    """
    Returns all free slots of the given duration on a specific date.
    date_iso should be 'YYYY-MM-DD'. Checks within working hours.
    """
    # Build day boundaries in IST
    tz_suffix = "+05:30"
    day_start = f"{date_iso}T{work_start_hour:02d}:00:00{tz_suffix}"
    day_end   = f"{date_iso}T{work_end_hour:02d}:00:00{tz_suffix}"

    body = {
        "timeMin": day_start,
        "timeMax": day_end,
        "timeZone": TIMEZONE,
        "items": [{"id": CALENDAR_ID}]
    }

    print(f"Fetching busy slots on {date_iso}...")
    try:
        result = service.freebusy().query(body=body).execute()
        busy_slots = result.get('calendars', {}).get(CALENDAR_ID, {}).get('busy', [])
    except Exception as e:
        return f"Error fetching calendar: {str(e)}"

    # Build busy intervals as datetime objects
    busy_intervals = []
    for slot in busy_slots:
        b_start = datetime.fromisoformat(slot['start'])
        b_end   = datetime.fromisoformat(slot['end'])
        busy_intervals.append((b_start, b_end))

    # Walk through the day in slot_duration_minutes steps
    current = datetime.fromisoformat(day_start)
    day_end_dt = datetime.fromisoformat(day_end)
    slot_delta = timedelta(minutes=slot_duration_minutes)
    free_slots = []

    while current + slot_delta <= day_end_dt:
        slot_end = current + slot_delta
        overlap = any(
            not (slot_end <= b[0] or current >= b[1])
            for b in busy_intervals
        )
        if not overlap:
            free_slots.append(
                f"{current.strftime('%I:%M %p')} – {slot_end.strftime('%I:%M %p')}"
            )
        current += slot_delta

    if not free_slots:
        return f"No available {slot_duration_minutes}-minute slots on {date_iso}."
    return (
        f"Available {slot_duration_minutes}-minute slots on {date_iso}:\n"
        + "\n".join(f"  • {s}" for s in free_slots)
    )


def view_waitlist(start_time_iso: str, end_time_iso: str) -> str:
    """Returns the waitlist for a specific slot."""
    waitlist = _load_waitlist()
    key = _slot_key(start_time_iso, end_time_iso)
    entries = waitlist.get(key, [])
    if not entries:
        return f"No one on the waitlist for {start_time_iso} to {end_time_iso}."
    lines = [f"  #{i+1}. {e['name']} ({e['phone']})" for i, e in enumerate(entries)]
    return f"Waitlist for {start_time_iso} – {end_time_iso}:\n" + "\n".join(lines)
