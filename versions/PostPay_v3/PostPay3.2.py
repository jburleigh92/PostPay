import os
import base64
import time
import json
import requests
import re
from datetime import datetime, timedelta, timezone
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import sqlite3
import pandas as pd

# Toggle for sleep mode
ENABLE_SLEEP_MODE = True  # Set to True to enable sleep mode, False to disable

# Define the scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Locking variables into the script
SLACK_WEBHOOK_URL = "REDACTED"
SLACK_API_TOKEN = "REDACTED"
SLACK_CHANNEL_ID = 'C065V16C18V'
CREDENTIALS_PATH = '/Users/jasonburleigh/postpay/programdirectory/credentials/paymentscredentials.json'
TOKEN_PATH = '/Users/jasonburleigh/postpay/programdirectory/token.json'
DATABASE_PATH = '/Users/jasonburleigh/postpay/programdirectory/payments.db'
MOCK_DB_PATH = '/Users/jasonburleigh/postpay/programdirectory/mock_chat.db'

# Define the time difference between UTC and PST (UTC-8)
PST_OFFSET = timedelta(hours=-8)

# SQLite database setup
def setup_database():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id TEXT PRIMARY KEY,
            provider TEXT,
            amount INTEGER,
            sender_name TEXT,
            date TEXT
        )
    ''')
    conn.commit()
    conn.close()

def log_payment(payment):
    if not is_payment_logged(payment['id']):
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO payments (id, provider, amount, sender_name, date) VALUES (?, ?, ?, ?, ?)
        ''', (payment['id'], payment['provider'], payment['amount'], payment['sender_name'], payment['date']))
        conn.commit()
        conn.close()
        print(f"Payment {payment['id']} added successfully.")
    else:
        print(f"Payment {payment['id']} already exists.")

def is_payment_logged(payment_id):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM payments WHERE id = ?', (payment_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

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
                        if sub_part['mimeType'] == 'text/plain']:
                            body = base64.urlsafe_b64decode(sub_part['body']['data']).decode('utf-8')

        return {
            'id': msg_id,
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
        return {msg.get('text', '') for msg in messages}
    return set()

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

def determine_provider(sender, body, subject):
    if 'venmo@venmo.com' in sender:
        return "Venmo"
    elif 'notify@cash.app' in sender or 'cash@square.com' in sender or 'cash app' in body.lower():
        return "Cash App"
    elif 'jason@bakedbudz.store' in sender:
        return "Cash App"
    elif 'apple' in body.lower() or 'apple' in subject.lower():
        return "Apple Cash"
    elif 'zelle' in body.lower() or 'zelle' in subject.lower():
        return "Zelle"
    else:
        return "Other"

def clean_subject(subject):
    subject = subject.split(' for from')[0].strip()
    return subject

def parse_payment_details(subject):
    try:
        parts = subject.split()
        amount_part = next(part for part in parts if '$' in part)
        amount = int(float(amount_part.replace('$', '').replace(',', '')))
        if 'sent' in parts:
            sender_name = " ".join(parts[:parts.index('sent')])
        elif 'paid' in parts:
            sender_name = " ".join(parts[:parts.index('paid')])
        else:
            sender_name = "Unknown"
        return amount, sender_name
    except (ValueError, StopIteration) as e:
        print(f"Error parsing payment details from subject '{subject}': {e}")
        return None, None

def write_database_to_excel():
    conn = sqlite3.connect(DATABASE_PATH)
    df = pd.read_sql_query("SELECT * FROM payments", conn)
    conn.close()
    
    excel_filename = "/Users/jasonburleigh/postpay/all_payments.xlsx"
    
    if os.path.exists(excel_filename):
        existing_df = pd.read_excel(excel_filename)
        combined_df = pd.concat([existing_df, df], ignore_index=True).drop_duplicates().reset_index(drop=True)
    else:
        combined_df = df
    
    combined_df.to_excel(excel_filename, index=False)
    print(f"The database has been written to {excel_filename}")

# Additional Zelle integration functions
def create_mock_imessage_db():
    conn = sqlite3.connect(MOCK_DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS message (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT
        )
    ''')
    messages = [
        "Chase | Zelle(R): MINAS M KARAGEZYAN sent you $110.00 & it's ready now. Reply STOP to cancel these texts.",
        "Zelle: JOHN DOE sent you $50.00.",
        "Jane sent you $75.00 via Zelle.",
        "Test user sent you $20.00 using Zelle."
    ]
    for message in messages:
        cursor.execute('''
            INSERT INTO message (text) VALUES (?)
        ''', (message,))
    conn.commit()
    conn.close()

def get_zelle_notifications():
    conn = sqlite3.connect(MOCK_DB_PATH)
    cursor = conn.cursor()
    
    # Query to get messages from the database
    cursor.execute("""
    SELECT text FROM message
    WHERE text LIKE '%Zelle%'
    ORDER BY id DESC
    LIMIT 10;
    """)
    
    messages = cursor.fetchall()
    conn.close()
    return [message[0] for message in messages]

def parse_zelle_notification(notification):
    try:
        match = re.search(r'(.+?) sent you \$(\d+\.\d{2})', notification)
        if match:
            sender_name = match.group(1).strip()
            amount = int(float(match.group(2).strip()))
            return sender_name, amount
        match = re.search(r'Chase \| Zelle\(R\): (.+?) sent you \$(\d+\.\d{2})', notification)
        if match:
            sender_name = match.group(1).strip()
            amount = int(float(match.group(2).strip()))
            return sender_name, amount
        return None, None
    except Exception as e:
        print(f"Error parsing Zelle notification: {e}")
        return None, None

def main():
    setup_database()
    creds = authenticate_gmail()
    service = build('gmail', 'v1', credentials=creds)
    
    posted_messages = get_posted_messages()

    create_mock_imessage_db()

    while True:
        # Get the current time in UTC and convert to PST
        current_time_utc = datetime.now(timezone.utc)
        current_time_pst = current_time_utc + PST_OFFSET
        current_hour_pst = current_time_pst.hour

        if ENABLE_SLEEP_MODE and (0 <= current_hour_pst < 9):
            print("Script paused. Writing database to Excel and sleeping until 9 AM PST...")
            write_database_to_excel()
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
            
            provider = determine_provider(sender, body, subject)
            amount, sender_name = parse_payment_details(subject)
            if amount is None or sender_name is None:
                continue

            formatted_message = f"{provider}: {sender_name} sent you ${amount}"

            if formatted_message not in posted_messages and not is_payment_logged(msg_id):
                print(f"Posting to Slack: {formatted_message}")
                post_to_slack(formatted_message)
                log_payment({
                    'id': msg_id,
                    'provider': provider,
                    'amount': amount,
                    'sender_name': sender_name,
                    'date': details['date']
                })
                posted_messages.add(formatted_message)  # Add to set to avoid duplicates
            else:
                print(f"Skipping duplicate message: {formatted_message}")
        
        # Zelle notification handling
        zelle_notifications = get_zelle_notifications()
        for notification in zelle_notifications:
            sender_name, amount = parse_zelle_notification(notification)
            if sender_name and amount:
                formatted_message = f"Zelle: {sender_name} sent you ${amount}"
                notification_id = f"zelle-{current_time_pst.timestamp()}"
                if formatted_message not in posted_messages and not is_payment_logged(notification_id):
                    print(f"Posting to Slack: {formatted_message}")
                    post_to_slack(formatted_message)
                    log_payment({
                        'id': notification_id,
                        'provider': 'Zelle',
                        'amount': amount,
                        'sender_name': sender_name,
                        'date': current_time_pst.isoformat()
                    })
                    posted_messages.add(formatted_message)  # Add to set to avoid duplicates
                else:
                    print(f"Skipping duplicate message: {formatted_message}")

        print("Sleeping for 30 seconds...")
        time.sleep(30)  # Wait for 30 seconds before checking again

if __name__ == '__main__':
    main()
