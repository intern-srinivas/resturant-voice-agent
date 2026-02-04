import logging
from fastapi import APIRouter, Request, Response
from config import config

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/answer")
@router.get("/answer")
async def answer_call(request: Request) -> Response:
    """
    Handle incoming calls from Plivo.

    Returns Plivo XML to:
    1. Speak a brief welcome
    2. Start bidirectional audio streaming via WebSocket
    """
    # Get call details from request
    form_data = await request.form() if request.method == "POST" else request.query_params
    call_uuid = form_data.get("CallUUID", "unknown")
    from_number = form_data.get("From", "unknown")

    logger.info(f"Incoming call: {call_uuid} from {from_number}")

    # Build WebSocket URL for audio streaming
    ws_url = config.SERVER_URL.replace("https://", "wss://").replace("http://", "ws://")
    stream_url = f"{ws_url}/stream/{call_uuid}"

    # Plivo XML response
    xml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Stream streamTimeout="86400" keepCallAlive="true" bidirectional="true" contentType="audio/x-mulaw;rate=8000" audioTrack="inbound">
        {stream_url}
    </Stream>
</Response>"""

    logger.info(f"Starting audio stream for call {call_uuid} at {stream_url}")

    return Response(content=xml_response, media_type="application/xml")


@router.post("/hangup")
async def handle_hangup(request: Request) -> dict:
    """Handle call hangup events."""
    form_data = await request.form()
    call_uuid = form_data.get("CallUUID", "unknown")

    logger.info(f"Call ended: {call_uuid}")

    return {"status": "ok"}


@router.post("/fallback")
async def handle_fallback(request: Request) -> Response:
    """Fallback handler if primary answer fails."""
    logger.warning("Fallback handler triggered")

    xml_response = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Speak>We're sorry, we're experiencing technical difficulties. Please try again later.</Speak>
    <Hangup/>
</Response>"""

    return Response(content=xml_response, media_type="application/xml")
