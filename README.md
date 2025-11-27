# PostPay (v4)
Automated payment-notification ingestion and Slack alerting system.

PostPay is a modular Python application that reads payment notification emails from Gmail, extracts structured payment data using provider-specific parsers, logs each payment to a SQLite database for deduplication, and posts formatted alerts to a Slack channel in real time.

This repository contains a cleaned and fully modularized version of the original PostPay4.py script, organized using standard Python project practices for maintainability, testing, and portfolio presentation.

---

## Features

PostPay replicates the exact functionality of the original script, including:

- Gmail API integration for reading recent payment-notification emails  
- Parsing logic for:
  - Zelle  
  - Venmo  
  - Cash App  
  - Apple Cash  
  - Generic “Other” payments  
- Regex-based extraction of amount, sender, and timestamp  
- SQLite logging of posted payments to prevent duplicates  
- Slack integration using `chat.postMessage`  
- Sleep mode between 00:00 and 09:00  
- 30-second configurable polling interval  
- Clean modular architecture  
- Full unit test coverage for parsers, Slack client, and importer logic  

No behavior has been added or changed from the original PostPay4.py beyond structural organization.

---

## Installation

Clone the repository:

```
git clone https://github.com/<your-username>/postpay.git
cd postpay
```

Create a Python virtual environment:

```
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```
pip install -r requirements.txt
```

---

## Configuration

All configuration is injected via environment variables.  
Create a `.env` file based on `.env.example`:

```
cp .env.example .env
```

Populate the following required values:

- `SLACK_API_TOKEN`
- `SLACK_CHANNEL_ID`
- `GMAIL_API_TOKEN`

Optional settings:

- `ENABLE_SLEEP_MODE`
- `POLL_INTERVAL_SECONDS`
- `GMAIL_SEARCH_QUERY`
- `DB_PATH`

The database file is created automatically on first run.

---

## Running PostPay

From the project root:

```
python src/main.py
```

The application will:

1. Load configuration  
2. Connect to SQLite  
3. Ensure schema exists  
4. Poll Gmail for recent messages  
5. Parse Zelle, Venmo, CashApp, Apple, or Other payments  
6. Deduplicate via database and runtime memory  
7. Post new payments to Slack  
8. Sleep 30 seconds and repeat  

---

## Testing

To run the full test suite:

```
python -m unittest discover tests
```

Tests validate:

- Parser correctness  
- Slack client request structure  
- Importer end-to-end logic including duplicates and DB persistence  

---

## Security Notes

- Do not commit your `.env` file.  
- OAuth tokens and Slack tokens must never be placed directly in source code.  
- `.gitignore` is configured to prevent accidental leaks of credentials or databases.

---

## License

PostPay is released under the MIT License.
