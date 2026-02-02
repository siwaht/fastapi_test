from fastapi import FastAPI
from pywa import WhatsApp
from pywa.types import Message
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI()

# WhatsApp configuration
wa = WhatsApp(
    phone_id=os.getenv("WHATSAPP_PHONE_ID"),
    token=os.getenv("WHATSAPP_TOKEN"),
    server=app,
    verify_token=os.getenv("WHATSAPP_VERIFY_TOKEN", "test"),
)

@wa.on_message()
def greet(client, message: Message):
    """Simple greeting handler."""
    message.reply_text(f"Hi {message.from_user.name}! 👋")

@app.get("/")
def root():
    return {"status": "ok", "message": "WhatsApp Bot is running"}

@app.get("/health")
def health():
    return {"status": "ok"}
