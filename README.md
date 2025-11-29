<p align="center">
  <img src="https://img.shields.io/github/v/tag/jburleigh92/PostPay?label=version&color=blue" />
  <img src="https://img.shields.io/github/actions/workflow/status/jburleigh92/PostPay/tests.yml?label=tests" />
  <img src="https://img.shields.io/github/license/jburleigh92/PostPay" />
</p>


# PostPay

PostPay is an automated payment-notification ingestion engine that reads payment alerts from Gmail, parses structured payment data (Zelle, Venmo, Cash App, Apple Cash), logs each payment into SQLite for deduplication, and posts formatted notifications to Slack in real time.

This repository is an industry-standard, fully modularized version of the original single-file PostPay4.py script, rewritten for clarity, maintainability, testing, and portfolio demonstration.

---

## Features

- Gmail API polling for recent payment-notification emails  
- Provider-specific parsers for:
  - Zelle  
  - Venmo  
  - Cash App  
  - Apple Cash  
  - Generic fallback (“Other”)  
- Regex-based extraction of amount, sender, timestamps  
- SQLite persistence + deduplication  
- Slack notifications using `chat.postMessage`  
- Optional sleep window (00:00–09:00)  
- Configurable polling interval  
- Clean domain-based architecture  
- Full unit test suite (parsers, importer, Gmail client, Slack client)

---

## Architecture Overview

```
PostPay/
│
├── data/
│   └── sample_emails.json
│
├── src/
│   └── postpay/
│       ├── db/
│       │   ├── connection.py            # SQLite connection helpers
│       │   ├── migrate.py               # Creates/updates schema
│       │   └── __init__.py
│       │
│       ├── parsers/                     # Provider-specific payment parsers
│       │   ├── apple_parser.py
│       │   ├── cashapp_parser.py
│       │   ├── other_parsers.py
│       │   ├── venmo_parser.py
│       │   ├── zelle_parser.py
│       │   └── __init__.py
│       │
│       ├── services/
│       │   ├── email/
│       │   │   └── gmail_client.py      # Gmail API wrapper
│       │   │
│       │   ├── notifications/
│       │   │   ├── formatter.py         # Slack-friendly formatting
│       │   │   └── slack.py             # Slack API posting
│       │   │
│       │   ├── payments/
│       │   │   ├── importer.py          # Import + dedupe + persistence
│       │   │   └── __init__.py
│       │   │
│       │   ├── scheduling/
│       │   │   ├── scheduler.py         # Sleep window scheduling
│       │   │   ├── sleep_window.py      # Window logic
│       │   │   └── __init__.py
│       │   │
│       │   └── __init__.py
│       │
│       ├── utils/
│       │   ├── logging_utils.py         # Lightweight logging helpers
│       │   ├── cli.py                   # Optional CLI entry
│       │   ├── config.py                # Environment/config loader
│       │   ├── logging.conf             # Logging configuration
│       │   ├── version.py               # Version constant
│       │   └── __init__.py
│       │
│       ├── main.py                      # Runtime entrypoint
│       └── __init__.py
│
├── tests/
│   ├── test_gmail_client.py
│   ├── test_importer.py
│   ├── test_parsers.py
│   ├── test_slack_client.py
│   └── __init__.py
│
├── requirements.txt                     # Python dependencies
├── pyproject.toml                       # Packaging + metadata
├── Makefile                             # Convenience tasks
├── README.md                            # Project documentation
├── VERSION                              # Version number (4.1.0)
└── LICENSE                              # MIT License
```

---

## Workflow Overview

1. GmailClient queries the Gmail API for recent messages matching the configured search query.  
2. Raw email bodies are extracted and passed to each provider parser.  
3. Parsers return structured objects containing:  
   - provider  
   - amount  
   - sender  
   - timestamp  
4. The importer checks SQLite for duplicates and writes new payments to the database.  
5. Each new payment is formatted and posted to Slack.  
6. If sleep mode is active, processing pauses between 00:00–09:00.  
7. The loop repeats on the configured interval.

---

## Installation

Clone the repository:

```bash
git clone https://github.com/<your-username>/PostPay.git
cd PostPay
```

Create a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Configuration

Configuration is provided via environment variables.  
Create a `.env` file based on the example:

```bash
cp .env.example .env
```

Update values such as:

- `SLACK_API_TOKEN`
- `SLACK_CHANNEL_ID`
- `GMAIL_TOKEN_PATH`
- `GMAIL_CREDENTIALS_PATH`
- `GMAIL_SEARCH_QUERY`
- `DB_PATH`
- `ENABLE_SLEEP_MODE`
- `POLL_INTERVAL_SECONDS`

The SQLite database is created automatically.

---

## Running PostPay

Run:

```bash
python src/postpay/main.py
```

This starts the continuous ingestion loop.

---

## Testing

Run the complete test suite:

```bash
python -m unittest discover tests
```

Tests include:

- Gmail client API behavior  
- Payment parsers  
- Importer logic (dedupe + DB)  
- Slack client request handling  

---

## Security Notes

- Do not commit `.env` or OAuth credentials.  
- `.gitignore` prevents checking in credential files or database files.  
- Tokens/keys must never be hard-coded.

---

## License

PostPay is released under the MIT License.
