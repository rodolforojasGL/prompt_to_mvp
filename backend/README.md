# Backend [WIP]

## Requirements
- Python 3.9+
- Gemini API key
- This readme assumes you are using MACOS.

## Getting Started

First create a file called .env inside the backend folder and add these variables (put your API key):

```
GOOGLE_API_KEY=
CHAT_MODEL=gemini-2.0-flash
OPENAI_CHAT_MODEL=
OPENAI_API_KEY=
ANTHROPIC_CHAT_MODEL=
ANTHROPIC_API_KEY=

HOST_IP=0.0.0.0
PORT_NUMBER=8000

API_BEARER_TOKENS=

CONNECTION_STRING=
DB_NAME=

HOST_IP=0.0.0.0
PORT_NUMBER=8000
```

Setup the Python's virtual environment 

```bash
backend % python -m venv .venv
backend % source .venv\bin\activate
backend % pip install -r requirements.txt
```

Run the server:

```bash
backend % cd src
backend % python main.py
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

## Learn More
