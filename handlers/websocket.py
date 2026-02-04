import asyncio
import base64
import json
import logging
from fastapi import WebSocket, WebSocketDisconnect
from services.deepgram_stt import DeepgramSTT
from services.elevenlabs_tts import ElevenLabsTTS
from services.openai_llm import OpenAILLM
from services.conversation import get_or_create_conversation, end_conversation

logger = logging.getLogger(__name__)


class CallSession:
    """Manages a single call session with all its components."""

    def __init__(self, call_id: str, plivo_ws: WebSocket):
        self.call_id = call_id
        self.plivo_ws = plivo_ws
        self.conversation = get_or_create_conversation(call_id)
        self.llm = OpenAILLM()
        self.tts = ElevenLabsTTS()
        self.stt: DeepgramSTT | None = None
        self.stream_id: str | None = None

        # Transcript accumulator for interim results
        self._current_transcript = ""
        self._processing_lock = asyncio.Lock()
        self._is_speaking = False
        self._final_received = asyncio.Event()
        self._stream_ready = asyncio.Event()

    async def initialize_services(self) -> None:
        """Initialize STT service."""
        self.stt = DeepgramSTT(
            on_transcript=self._on_transcript,
            on_error=self._on_stt_error,
        )
        await self.stt.connect()

    async def on_stream_start(self, stream_id: str) -> None:
        """Called when Plivo stream is ready."""
        self.stream_id = stream_id
        self._stream_ready.set()
        logger.info(f"Stream ready for call {self.call_id}, stream_id: {stream_id}")

        # Now send the greeting
        greeting = await self.llm.get_greeting(self.conversation)
        await self._speak(greeting)

    async def handle_audio(self, audio_data: bytes) -> None:
        """Process incoming audio from Plivo."""
        if self.stt and self.stt.is_connected:
            await self.stt.send_audio(audio_data)

    def _on_transcript(self, text: str, is_final: bool) -> None:
        """Handle transcription results from Deepgram."""
        if is_final:
            self._current_transcript = text
            self._final_received.set()
            logger.info(f"Final transcript: {text}")
        else:
            self._current_transcript = text
            logger.debug(f"Interim transcript: {text}")

    def _on_stt_error(self, error: Exception) -> None:
        """Handle STT errors."""
        logger.error(f"STT error in call {self.call_id}: {error}")

    async def process_user_input(self) -> None:
        """Wait for user input and generate response."""
        # Wait for stream to be ready first
        await self._stream_ready.wait()

        while True:
            try:
                self._final_received.clear()
                await asyncio.wait_for(self._final_received.wait(), timeout=30.0)

                transcript = self._current_transcript.strip()
                if not transcript:
                    continue

                self._current_transcript = ""

                if self._is_speaking:
                    logger.debug("Ignoring input while speaking")
                    continue

                logger.info(f"Processing user input: {transcript}")

                response = await self.llm.get_response(self.conversation, transcript)
                await self._speak(response)

                if self.conversation.reservation.is_complete():
                    if not self.conversation.reservation.confirmed:
                        logger.info(
                            f"Reservation complete: {self.conversation.reservation.to_summary()}"
                        )

            except asyncio.TimeoutError:
                logger.info("No user input detected, waiting...")
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error processing user input: {e}")

    async def _speak(self, text: str) -> None:
        """Convert text to speech and send to caller."""
        if not text.strip():
            return

        async with self._processing_lock:
            self._is_speaking = True
            try:
                audio_data = await self.tts.synthesize(text)

                if audio_data:
                    await self._send_audio_to_plivo(audio_data)

                    # Wait for audio to play
                    duration = len(audio_data) / 8000
                    await asyncio.sleep(duration + 0.5)

            except Exception as e:
                logger.error(f"Error speaking: {e}")
            finally:
                self._is_speaking = False

    async def _send_audio_to_plivo(self, audio_data: bytes) -> None:
        """Send audio data to Plivo WebSocket."""
        if not self._stream_ready.is_set():
            logger.warning("Attempted to send audio before stream ready")
            return

        try:
            # Send audio in Plivo's expected format
            # See: https://support.plivo.com/hc/en-us/articles/32252710653337
            encoded = base64.b64encode(audio_data).decode("utf-8")

            message = json.dumps({
                "event": "playAudio",
                "media": {
                    "contentType": "audio/x-mulaw",
                    "sampleRate": 8000,
                    "payload": encoded,
                }
            })

            logger.info(f"Sending audio to Plivo: {len(audio_data)} bytes")
            await self.plivo_ws.send_text(message)

        except Exception as e:
            logger.error(f"Error sending audio to Plivo: {e}")

    async def close(self) -> None:
        """Clean up session resources."""
        if self.stt:
            await self.stt.close()
        await self.tts.close()
        end_conversation(self.call_id)
        logger.info(f"Session {self.call_id} closed")


async def handle_plivo_stream(websocket: WebSocket, call_id: str) -> None:
    """
    Handle WebSocket connection from Plivo for audio streaming.
    """
    await websocket.accept()
    logger.info(f"WebSocket connected for call: {call_id}")

    session = CallSession(call_id, websocket)
    process_task = None

    try:
        # Initialize services (but don't send greeting yet)
        await session.initialize_services()

        # Start processing task (will wait for stream ready)
        process_task = asyncio.create_task(session.process_user_input())

        # Main loop to receive messages from Plivo
        while True:
            try:
                message = await websocket.receive_text()
                data = json.loads(message)
                event = data.get("event")

                logger.debug(f"Received Plivo event: {event}")

                if event == "start":
                    # Stream is ready - extract stream ID and send greeting
                    stream_id = data.get("start", {}).get("streamId", call_id)
                    logger.info(f"Stream started for call {call_id}")
                    await session.on_stream_start(stream_id)

                elif event == "media":
                    media = data.get("media", {})
                    payload = media.get("payload", "")

                    if payload:
                        audio_data = base64.b64decode(payload)
                        await session.handle_audio(audio_data)

                elif event == "stop":
                    logger.info(f"Stream stopped for call {call_id}")
                    break

                elif event == "connected":
                    logger.info(f"Plivo WebSocket connected for call {call_id}")

            except json.JSONDecodeError:
                logger.warning("Received non-JSON message from Plivo")
            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected for call {call_id}")
                break

    except WebSocketDisconnect:
        logger.info(f"Call {call_id} disconnected")
    except Exception as e:
        logger.error(f"Error in WebSocket handler for call {call_id}: {e}")
    finally:
        if process_task:
            process_task.cancel()
            try:
                await process_task
            except asyncio.CancelledError:
                pass
        await session.close()
        logger.info(f"WebSocket handler closed for call {call_id}")
