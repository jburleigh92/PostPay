# PostPay (4.1.0)
Automated payment-notification ingestion and Slack alerting system.

PostPay is a modular Python application that reads payment notification emails from Gmail, extracts structured payment data using provider-specific parsers, logs each payment to a SQLite database for deduplication, and posts formatted alerts to a Slack channel in real time.

This repository contains a cleaned and fully modularized version of the original PostPay4.py script, organized using standard Python project patterns for maintainability, testing, and portfolio presentation.

---

## Features

PostPay implements the same functional logic as the original script, including:

- Gmail API integration for reading recent payment-notification emails  
- Parsing logic for:
  - Zelle  
  - Venmo  
  - Cash App  
  - Apple Cash  
  - Generic "Other" payments  
- Regex-based extraction of amount, sender, and timestamp  
- SQLite logging of posted payments to prevent duplicates  
- Slack integration using chat.postMessage  
- Sleep mode between 00:00 and 09:00  
- 30-second configurable polling interval  
- Modular, testable architecture  
- Unit test coverage for parsers, Slack client, Gmail client, and importer logic  

No business behavior was changed. Only the structure was modernized.

---

## Installation

Clone the repository:

git clone https://github.com/<your-username>/postpay.git
cd postpay

Create and activate a virtual environment:

python3 -m venv venv 
source venv/bin/activate

Install dependencies:

pip install -r requirements.txt

---

## Configuration

All configuration is loaded from environment variables.
Create a `.env` file based on `.env.example`:

cp .env.example .env

Required values:

- SLACK_API_TOKEN  
- SLACK_CHANNEL_ID  
- GMAIL_TOKEN_PATH  
- GMAIL_CREDENTIALS_PATH  
- GMAIL_SEARCH_QUERY  

Optional settings:

- ENABLE_SLEEP_MODE  
- POLL_INTERVAL_SECONDS  
- DB_PATH  

A SQLite database is created automatically on first run.

---

## Running PostPay

Run the application from the project root:

python src/postpay/main.py

The service will:

1. Load configuration  
2. Initialize the SQLite schema  
3. Authenticate to the Gmail API  
4. Fetch recent messages matching the search query  
5. Parse Zelle, Venmo, Cash App, Apple Cash, or Other payments  
6. Deduplicate using both the database and in-memory runtime cache  
7. Post new payments to Slack  
8. Sleep for the configured interval and repeat  

---

## Testing

Run the full test suite:

python -m unittest discover src/postpay/tests

The test suite validates:

- All payment parsers  
- Slack client request construction  
- Gmail client message extraction  
- Payment importer end-to-end logic including DB persistence and duplicate detection  

---

## Security Notes

- Never commit `.env` files or any API tokens  
- OAuth tokens and Slack tokens must remain outside source control  
- `.gitignore` is configured to prevent accidental leaks of credentials or local SQLite databases  

---

## License

Released under the MIT License.
