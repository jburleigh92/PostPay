import os
import base64
import time
import json
import requests
from datetime import datetime, timedelta, timezone
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Define the scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL')
SLACK_API_TOKEN = os.getenv('SLACK_API_TOKEN')
SLACK_CHANNEL_ID = os.getenv('SLACK_CHANNEL_ID')

# Specify the paths for credentials and token files
CREDENTIALS_PATH = os.getenv('CREDENTIALS_PATH')
TOKEN_PATH = os.getenv('TOKEN_PATH')

# Define the time difference between UTC and PST (UTC-8)
PST_OFFSET = timedelta(hours=-8)

def authenticate_gmail():
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())
    return creds

def get_payment_emails(service, user_id='me'):
    queries = [
        'from:venmo@venmo.com',
        'from:notify@cash.app',
        'from:cash@square.com',
        'from:jason@bakedbudz.store'
    ]
    messages = []
    for query in queries:
        try:
            results = service.users().messages().list(userId=user_id, q=query).execute()
            query_messages = results.get('messages', [])
            print(f"Found {len(query_messages)} messages for query '{query}'.")
            messages.extend(query_messages)
        except Exception as e:
            print(f"Error fetching emails for query '{query}': {e}")
    return messages

def get_email_details(service, msg_id, user_id='me'):
    try:
        message = service.users().messages().get(userId=user_id, id=msg_id, format='full').execute()
        payload = message.get('payload', {})
        headers = payload.get('headers', [])
        
        subject = None
        date = None
        sender = None
        for header in headers:
            if header['name'] == 'Subject':
                subject = header['value']
            if header['name'] == 'Date':
                date = header['value']
            if header['name'] == 'From':
                sender = header['value']

        internal_date = message.get('internalDate', 0)
        body = ''
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                elif 'parts' in part:
                    for sub_part in part['parts']:
                        if sub_part['mimeType'] == 'text/plain':
                            body = base64.urlsafe_b64decode(sub_part['body']['data']).decode('utf-8')

        print(f"Email Subject: {subject}, Internal Date: {internal_date}, Body: {body[:100]}...")
        return {
            'subject': subject,
            'internal_date': internal_date,
            'date': date,
            'sender': sender,
            'body': body
        }
    except Exception as e:
        print(f"Error fetching email details: {e}")
        return None

def get_posted_messages():
    url = 'https://slack.com/api/conversations.history'
    headers = {
        'Authorization': f'Bearer {SLACK_API_TOKEN}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    params = {
        'channel': SLACK_CHANNEL_ID,
        'limit': 100
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        messages = response.json().get('messages', [])
        return [msg.get('text', '') for msg in messages]
    return []

def post_to_slack(message):
    headers = {'Content-type': 'application/json'}
    payload = {'text': message}
    response = requests.post(SLACK_WEBHOOK_URL, headers=headers, json=payload)
    if response.status_code == 404:
        print(f"Error: 404 Not Found - Check the Slack webhook URL.")
    if response.status_code != 200:
        print(f"Error response from Slack: {response.text}")
        raise ValueError(f'Request to Slack returned an error {response.status_code}, the response is:\n{response.text}')
    print("Message posted to Slack successfully.")

def is_today(timestamp):
    email_date = datetime.fromtimestamp(timestamp / 1000)
    today = datetime.now()
    return email_date.date() == today.date()

def determine_prefix(sender, body, subject):
    if 'venmo@venmo.com' in sender:
        return "Venmo: "
    elif 'notify@cash.app' in sender or 'cash@square.com' in sender or 'cash app' in body.lower():
        return "Cash App: "
    elif 'jason@bakedbudz.store' in sender:
        return "Cash App: "
    elif 'apple' in body.lower() or 'apple' in subject.lower():
        return "Apple Cash: "
    elif 'zelle' in body.lower() or 'zelle' in subject.lower():
        return "Zelle: "
    else:
        return "Other: "

def clean_subject(subject):
    subject = subject.split(' for from')[0].strip()
    return subject

def main():
    creds = authenticate_gmail()
    service = build('gmail', 'v1', credentials=creds)
    
    posted_messages = get_posted_messages()

    while True:
        # Get the current time in UTC and convert to PST
        current_time_utc = datetime.now(timezone.utc)
        current_time_pst = current_time_utc + PST_OFFSET
        current_hour_pst = current_time_pst.hour

        if 0 <= current_hour_pst < 9:
            print("Script paused. Sleeping until 9 AM PST...")
            time.sleep(60 * 60)  # Sleep for 1 hour
            continue

        messages = get_payment_emails(service)
        for message in messages:
            msg_id = message['id']
            details = get_email_details(service, msg_id)
            if details is None:
                continue

            internal_date = int(details['internal_date'])
            subject = details['subject']
            body = details['body']
            sender = details['sender']

            if not is_today(internal_date):
                continue

            if any(keyword in subject.lower() for keyword in ['transfer', 'dispute', 'request']):
                continue

            # Omit outgoing payments
            if 'you sent' in subject.lower():
                continue
            
            prefix = determine_prefix(sender, body, subject)
            subject = clean_subject(subject)
            formatted_message = f"{prefix}{subject}"

            if formatted_message not in posted_messages:
                print(f"Posting to Slack: {formatted_message}")
                post_to_slack(formatted_message)
                posted_messages.append(formatted_message)
            else:
                print(f"Skipping duplicate message: {formatted_message}")
        
        print("Sleeping for 30 seconds...")
        time.sleep(30)  # Wait for 30 seconds before checking again

if __name__ == '__main__':
    main()
