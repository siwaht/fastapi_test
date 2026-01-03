import os
import logging
from fastapi import FastAPI
from pywa import WhatsApp, filters
from pywa.types import Message
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI()

# Get environment variables
phone_id = os.getenv("WHATSAPP_PHONE_ID")
token = os.getenv("WHATSAPP_TOKEN")
verify_token = os.getenv("WHATSAPP_VERIFY_TOKEN", "change-me")
app_secret = os.getenv("WHATSAPP_APP_SECRET")  # Optional: for signature validation

# Validate required environment variables
if not phone_id or not token:
    raise ValueError("WHATSAPP_PHONE_ID and WHATSAPP_TOKEN must be set")

# Initialize WhatsApp client
wa = WhatsApp(
    phone_id=phone_id,
    token=token,
    server=app,
    verify_token=verify_token,
    app_secret=app_secret,  # Set to None if not provided (signature validation disabled)
    validate_updates=bool(app_secret),  # Only validate if app_secret is provided
)

@wa.on_raw_update()
def raw_update_handler(client: WhatsApp, update: dict):
    """Debug: log all incoming updates"""
    logger.info(f"Raw update received: {update}")

@wa.on_message(filters.text)
def greet_handler(client: WhatsApp, msg: Message):
    """Simple greeting bot"""
    logger.info(f"Received message from {msg.from_user.name}: {msg.text}")
    try:
        msg.react("👋")
        msg.reply_text(f"Hi {msg.from_user.name}! How are you?")
        logger.info(f"Sent reply to {msg.from_user.name}")
    except Exception as e:
        logger.error(f"Error handling message: {e}")

@app.get("/")
def root():
    return {"status": "ok", "message": "PyWa WhatsApp bot is running"}

@app.get("/health")
def health():
    return {"status": "ok"}

