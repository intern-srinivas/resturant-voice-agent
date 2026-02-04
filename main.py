import logging
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from handlers.plivo_webhook import router as plivo_router
from handlers.websocket import handle_plivo_stream
from config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Mario's Italian Kitchen - Voice Reservation Agent",
    description="AI-powered voice agent for restaurant reservations",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Plivo webhook routes
app.include_router(plivo_router, tags=["Plivo Webhooks"])


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "running",
        "service": "Mario's Italian Kitchen Voice Agent",
        "version": "1.0.0",
    }


@app.get("/health")
async def health_check():
    """Health check for monitoring."""
    return {"status": "healthy"}


@app.websocket("/stream/{call_id}")
async def websocket_endpoint(websocket: WebSocket, call_id: str):
    """WebSocket endpoint for Plivo audio streaming."""
    await handle_plivo_stream(websocket, call_id)


@app.on_event("startup")
async def startup_event():
    """Application startup tasks."""
    logger.info("=" * 50)
    logger.info("Starting Voice AI Agent Server")
    logger.info(f"Server URL: {config.SERVER_URL}")
    logger.info("=" * 50)

    # Validate configuration
    missing = []
    if not config.PLIVO_AUTH_ID:
        missing.append("PLIVO_AUTH_ID")
    if not config.PLIVO_AUTH_TOKEN:
        missing.append("PLIVO_AUTH_TOKEN")
    if not config.DEEPGRAM_API_KEY:
        missing.append("DEEPGRAM_API_KEY")
    if not config.ELEVENLABS_API_KEY:
        missing.append("ELEVENLABS_API_KEY")
    if not config.OPENAI_API_KEY:
        missing.append("OPENAI_API_KEY")

    if missing:
        logger.warning(f"Missing configuration: {', '.join(missing)}")
        logger.warning("Please set these in your .env file")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown tasks."""
    logger.info("Shutting down Voice AI Agent Server")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=config.HOST,
        port=config.PORT,
        reload=True,
        log_level="info",
    )
