# Voice AI Agent - Restaurant Reservation System

AI-powered voice agent that handles inbound calls for restaurant reservations using Plivo, Deepgram (STT), Cartesia (TTS), and OpenAI GPT-4.

## Architecture

```
Inbound Call → Plivo → WebSocket → Deepgram STT → OpenAI GPT-4 → Cartesia TTS → Caller
```

## Features

- Real-time speech-to-text transcription
- Natural language understanding for reservation booking
- Human-like voice responses with streaming TTS
- Conversation state tracking (date, time, party size, name)
- Graceful error handling

## Quick Start

### 1. Clone and Install

```bash
git clone https://github.com/intern-srinivas/resturant-voice-agent.git
cd resturant-voice-agent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your API keys:
- `PLIVO_AUTH_ID` - From Plivo Console
- `PLIVO_AUTH_TOKEN` - From Plivo Console
- `DEEPGRAM_API_KEY` - From Deepgram Console
- `CARTESIA_API_KEY` - From Cartesia
- `OPENAI_API_KEY` - From OpenAI Platform
- `SERVER_URL` - Your deployment URL

### 3. Run Locally (Development)

```bash
# Start ngrok tunnel
ngrok http 8000

# Update SERVER_URL in .env with ngrok URL

# Run the server
python main.py
```

### 4. Configure Plivo Webhooks

1. Go to [Plivo Console](https://console.plivo.com/)
2. Navigate to Phone Numbers → Your Number
3. Set Answer URL: `https://your-url/answer`
4. Set Hangup URL: `https://your-url/hangup`

## Deploy to Render

1. Push code to GitHub
2. Go to [render.com](https://render.com) → New Web Service
3. Connect your GitHub repo
4. Configure:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables in the Environment tab
6. Deploy and update Plivo webhooks with Render URL

## Project Structure

```
├── main.py                 # FastAPI application entry point
├── config.py               # Configuration management
├── requirements.txt        # Python dependencies
├── render.yaml             # Render deployment config
├── handlers/
│   ├── plivo_webhook.py    # Plivo webhook handlers
│   └── websocket.py        # WebSocket audio streaming
├── services/
│   ├── conversation.py     # Conversation state management
│   ├── deepgram_stt.py     # Deepgram speech-to-text
│   ├── cartesia_tts.py     # Cartesia text-to-speech
│   └── openai_llm.py       # OpenAI conversation handler
└── utils/
    └── audio.py            # Audio conversion utilities
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/health` | GET | Health status |
| `/answer` | POST | Plivo call answer webhook |
| `/hangup` | POST | Plivo hangup webhook |
| `/stream/{call_id}` | WebSocket | Audio streaming |

## Conversation Flow

1. Agent greets caller: *"Hi, thanks for calling Mario's Italian Kitchen!"*
2. Collects reservation date
3. Collects preferred time
4. Collects party size
5. Collects name for reservation
6. Confirms complete reservation details

## Tech Stack

- **Backend:** Python, FastAPI
- **Telephony:** Plivo Voice API
- **Speech-to-Text:** Deepgram Nova-2
- **Text-to-Speech:** Cartesia Sonic-3
- **LLM:** OpenAI GPT-4o-mini
- **Hosting:** Render
