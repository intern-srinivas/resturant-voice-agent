import logging
from typing import AsyncIterator
from cartesia import AsyncCartesia
from config import config

logger = logging.getLogger(__name__)


class CartesiaTTS:
    """Cartesia Text-to-Speech service."""

    def __init__(self, voice_id: str = "7ea5e9c2-b719-4dc3-b870-5ba5f14d31d8"):
        """
        Initialize Cartesia TTS.

        Args:
            voice_id: Cartesia voice ID (default: custom cloned voice)
                     Browse voices at: https://play.cartesia.ai/
        """
        self.voice_id = voice_id
        self.client = AsyncCartesia(api_key=config.CARTESIA_API_KEY)
        self.model_id = "sonic-3"  # Fastest model: 40-90ms TTFA

    async def synthesize(self, text: str) -> bytes:
        """Convert text to speech audio in mulaw 8kHz format."""
        if not text.strip():
            return b""

        try:
            audio_chunks = []

            async for chunk in self.client.tts.bytes(
                model_id=self.model_id,
                transcript=text,
                voice={"mode": "id", "id": self.voice_id},
                language="en",
                output_format={
                    "container": "raw",
                    "encoding": "pcm_mulaw",
                    "sample_rate": 8000,
                },
            ):
                audio_chunks.append(chunk)

            audio_data = b"".join(audio_chunks)
            logger.info(f"Generated TTS audio: {len(audio_data)} bytes")
            return audio_data

        except Exception as e:
            logger.error(f"Cartesia TTS error: {e}")
            raise

    async def synthesize_stream(self, text: str) -> AsyncIterator[bytes]:
        """Stream audio chunks as they arrive for lower latency."""
        if not text.strip():
            return

        try:
            async for chunk in self.client.tts.bytes(
                model_id=self.model_id,
                transcript=text,
                voice={"mode": "id", "id": self.voice_id},
                language="en",
                output_format={
                    "container": "raw",
                    "encoding": "pcm_mulaw",
                    "sample_rate": 8000,
                },
            ):
                yield chunk

        except Exception as e:
            logger.error(f"Cartesia TTS streaming error: {e}")
            raise

    async def close(self) -> None:
        """Close the Cartesia client."""
        await self.client.close()
        logger.info("Cartesia TTS client closed")
