import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Plivo
    PLIVO_AUTH_ID: str = os.getenv("PLIVO_AUTH_ID", "")
    PLIVO_AUTH_TOKEN: str = os.getenv("PLIVO_AUTH_TOKEN", "")
    PLIVO_PHONE_NUMBER: str = os.getenv("PLIVO_PHONE_NUMBER", "")

    # Deepgram
    DEEPGRAM_API_KEY: str = os.getenv("DEEPGRAM_API_KEY", "")

    # ElevenLabs
    ELEVENLABS_API_KEY: str = os.getenv("ELEVENLABS_API_KEY", "")

    # Cartesia
    CARTESIA_API_KEY: str = os.getenv("CARTESIA_API_KEY", "")

    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # Server
    SERVER_URL: str = os.getenv("SERVER_URL", "http://localhost:8000")
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))

    # Railway sets RAILWAY_PUBLIC_DOMAIN automatically
    RAILWAY_URL: str = os.getenv("RAILWAY_PUBLIC_DOMAIN", "")

    # Audio settings for Plivo
    AUDIO_ENCODING: str = "mulaw"
    SAMPLE_RATE: int = 8000


config = Config()
