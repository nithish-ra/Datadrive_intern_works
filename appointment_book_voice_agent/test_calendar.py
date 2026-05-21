import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build

# 1. Update this if your JSON file has a different name
SERVICE_ACCOUNT_FILE = 'Key.json'

# 2. This is the calendar you just shared
CALENDAR_ID = 'nithish2370014@ssn.edu.in' 

SCOPES = ['https://www.googleapis.com/auth/calendar']

def test_connection():
    print("Attempting to authenticate with Google Cloud...")
    try:
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        service = build('calendar', 'v3', credentials=creds)
        print("Authentication successful!")
    except Exception as e:
        print(f"Authentication failed. Check your JSON file path.\nError: {e}")
        return

    print(f"Querying upcoming events for {CALENDAR_ID}...")
    try:
        now = datetime.datetime.utcnow().isoformat() + 'Z'  
        
        events_result = service.events().list(
            calendarId=CALENDAR_ID, 
            timeMin=now,
            maxResults=3, 
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])

        if not events:
            print('\n🎉 Success! Connected perfectly. Your calendar is currently empty.')
        else:
            print('\n🎉 Success! Connected perfectly. Here are your next scheduled slots:')
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                print(f"- {start}: {event.get('summary', 'Untitled Event')}")

    except Exception as e:
        print(f"\nConnection failed. \nError details: {e}")

if __name__ == '__main__':
    test_connection()

# grok api key 
# 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