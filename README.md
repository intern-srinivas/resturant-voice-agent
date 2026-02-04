# Mario's Italian Kitchen - Voice Reservation Agent

AI-powered voice agent that handles inbound calls for restaurant reservations using Plivo, Deepgram (STT), ElevenLabs (TTS), and OpenAI.

## Architecture

```
Inbound Call → Plivo → WebSocket → Deepgram STT → OpenAI GPT-4 → ElevenLabs TTS → Caller
```

## Setup

### 1. Install Dependencies

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```
PLIVO_AUTH_ID=your_plivo_auth_id
PLIVO_AUTH_TOKEN=your_plivo_auth_token
PLIVO_PHONE_NUMBER=your_plivo_phone_number
DEEPGRAM_API_KEY=your_deepgram_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
OPENAI_API_KEY=your_openai_api_key
SERVER_URL=https://your-ngrok-url.ngrok.io
```

### 3. Expose Local Server (for development)

```bash
ngrok http 8000
```

Copy the HTTPS URL and update `SERVER_URL` in your `.env` file.

### 4. Configure Plivo

1. Go to [Plivo Console](https://console.plivo.com/)
2. Navigate to Phone Numbers → Your Number
3. Set the Answer URL to: `https://your-ngrok-url.ngrok.io/answer`
4. Set the Hangup URL to: `https://your-ngrok-url.ngrok.io/hangup`

### 5. Run the Server

```bash
python main.py
# or
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Usage

1. Call your Plivo phone number
2. The agent will greet you and ask for reservation details
3. Provide: date, time, party size, and name
4. The agent will confirm your reservation

## Project Structure

```
├── main.py                 # FastAPI application entry point
├── config.py               # Configuration management
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── handlers/
│   ├── plivo_webhook.py   # Plivo webhook handlers
│   └── websocket.py       # WebSocket audio streaming handler
├── services/
│   ├── conversation.py    # Conversation state management
│   ├── deepgram_stt.py    # Speech-to-text service (Deepgram)
│   ├── elevenlabs_tts.py  # Text-to-speech service (ElevenLabs)
│   └── openai_llm.py      # LLM conversation handler
└── utils/
    └── audio.py           # Audio conversion utilities
```

## API Endpoints

- `GET /` - Health check
- `GET /health` - Health status
- `POST /answer` - Plivo call answer webhook
- `POST /hangup` - Plivo hangup webhook
- `WS /stream/{call_id}` - WebSocket for audio streaming

## Conversation Flow

1. Agent greets caller
2. Asks for reservation date
3. Asks for time preference
4. Suggests available times
5. Asks for party size
6. Asks for name
7. Confirms complete reservation
