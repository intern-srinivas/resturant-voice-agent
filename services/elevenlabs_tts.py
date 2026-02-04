import logging
import httpx
from config import config

logger = logging.getLogger(__name__)


class ElevenLabsTTS:
    """ElevenLabs Text-to-Speech service."""

    ELEVENLABS_API_URL = "https://api.elevenlabs.io/v1/text-to-speech"

    def __init__(self, voice_id: str = "21m00Tcm4TlvDq8ikWAM"):
        """
        Initialize ElevenLabs TTS.

        Args:
            voice_id: ElevenLabs voice ID (default: Rachel - conversational voice)
                     Other options:
                     - 21m00Tcm4TlvDq8ikWAM (Rachel)
                     - EXAVITQu4vr4xnSDxMaL (Bella)
                     - ErXwobaYiN019PkySvjV (Antoni)
                     - MF3mGyEYCl7XYWbV9V6O (Elli)
        """
        self.voice_id = voice_id
        self.client = httpx.AsyncClient(timeout=30.0)

    async def synthesize(self, text: str) -> bytes:
        """
        Convert text to speech audio.

        Args:
            text: Text to convert to speech

        Returns:
            Audio data in mulaw format (8kHz)
        """
        if not text.strip():
            return b""

        url = f"{self.ELEVENLABS_API_URL}/{self.voice_id}"

        headers = {
            "xi-api-key": config.ELEVENLABS_API_KEY,
            "Content-Type": "application/json",
            "Accept": "audio/basic",  # mulaw format
        }

        payload = {
            "text": text,
            "model_id": "eleven_turbo_v2",  # Faster, lower latency model
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.0,
                "use_speaker_boost": True,
            },
        }

        # Query params for output format
        params = {
            "output_format": "ulaw_8000",  # mulaw at 8kHz for Plivo
        }

        try:
            response = await self.client.post(
                url, headers=headers, json=payload, params=params
            )
            response.raise_for_status()

            audio_data = response.content
            logger.info(
                f"Generated TTS audio: {len(audio_data)} bytes for '{text[:50]}...'"
            )
            return audio_data

        except httpx.HTTPStatusError as e:
            logger.error(
                f"ElevenLabs TTS HTTP error: {e.response.status_code} - {e.response.text}"
            )
            raise
        except Exception as e:
            logger.error(f"ElevenLabs TTS error: {e}")
            raise

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()
        logger.info("ElevenLabs TTS client closed")
