import asyncio
import json
import logging
from typing import Callable, Optional
import websockets
from config import config

logger = logging.getLogger(__name__)


class DeepgramSTT:
    """Deepgram Speech-to-Text service using WebSocket streaming."""

    DEEPGRAM_WS_URL = "wss://api.deepgram.com/v1/listen"

    def __init__(
        self,
        on_transcript: Callable[[str, bool], None],
        on_error: Optional[Callable[[Exception], None]] = None,
    ):
        """
        Initialize Deepgram STT.

        Args:
            on_transcript: Callback for transcription results (text, is_final)
            on_error: Optional callback for errors
        """
        self.on_transcript = on_transcript
        self.on_error = on_error or (lambda e: logger.error(f"STT error: {e}"))
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self._connected = False
        self._receive_task: Optional[asyncio.Task] = None

    def _build_url(self) -> str:
        """Build the Deepgram WebSocket URL with parameters."""
        params = [
            "model=nova-2",
            "encoding=mulaw",
            "sample_rate=8000",
            "channels=1",
            "punctuate=true",
            "interim_results=true",
            "endpointing=300",
            "utterance_end_ms=1000",
        ]
        return f"{self.DEEPGRAM_WS_URL}?{'&'.join(params)}"

    async def connect(self) -> None:
        """Establish connection to Deepgram."""
        if self._connected:
            return

        url = self._build_url()
        headers = {"Authorization": f"Token {config.DEEPGRAM_API_KEY}"}

        try:
            self.ws = await websockets.connect(url, extra_headers=headers)
            self._connected = True
            self._receive_task = asyncio.create_task(self._receive_loop())
            logger.info("Connected to Deepgram STT")
        except Exception as e:
            logger.error(f"Failed to connect to Deepgram: {e}")
            raise

    async def _receive_loop(self) -> None:
        """Listen for transcription results from Deepgram."""
        if not self.ws:
            return

        try:
            async for message in self.ws:
                try:
                    data = json.loads(message)
                    self._handle_message(data)
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON from Deepgram: {message}")
        except websockets.exceptions.ConnectionClosed:
            logger.info("Deepgram connection closed")
        except Exception as e:
            self.on_error(e)
        finally:
            self._connected = False

    def _handle_message(self, data: dict) -> None:
        """Process a message from Deepgram."""
        msg_type = data.get("type")

        if msg_type == "Results":
            channel = data.get("channel", {})
            alternatives = channel.get("alternatives", [])

            if alternatives:
                transcript = alternatives[0].get("transcript", "")
                is_final = data.get("is_final", False)

                if transcript.strip():
                    logger.debug(
                        f"Transcript ({'final' if is_final else 'interim'}): {transcript}"
                    )
                    self.on_transcript(transcript, is_final)

        elif msg_type == "UtteranceEnd":
            logger.debug("Utterance end detected")

        elif msg_type == "Error":
            error_msg = data.get("message", "Unknown error")
            logger.error(f"Deepgram error: {error_msg}")

    async def send_audio(self, audio_data: bytes) -> None:
        """Send audio data to Deepgram for transcription."""
        if not self._connected or not self.ws:
            logger.warning("Cannot send audio: not connected")
            return

        try:
            await self.ws.send(audio_data)
        except Exception as e:
            logger.error(f"Error sending audio to Deepgram: {e}")
            self.on_error(e)

    async def close(self) -> None:
        """Close the Deepgram connection."""
        self._connected = False

        if self.ws:
            try:
                # Send close message to Deepgram
                await self.ws.send(json.dumps({"type": "CloseStream"}))
                await self.ws.close()
            except Exception as e:
                logger.error(f"Error closing Deepgram connection: {e}")

        if self._receive_task:
            self._receive_task.cancel()
            try:
                await self._receive_task
            except asyncio.CancelledError:
                pass

        logger.info("Deepgram STT connection closed")

    @property
    def is_connected(self) -> bool:
        """Check if connected to Deepgram."""
        return self._connected
