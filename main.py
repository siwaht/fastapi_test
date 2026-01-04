from fastapi import FastAPI
from pywa import WhatsApp, filters
from pywa.types import Message, CallbackButton
import logging
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Global dictionary to store user state
sessions = {}

# Configure logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI()

# WhatsApp configuration
wa = WhatsApp(
    phone_id=os.getenv("WHATSAPP_PHONE_ID"),
    token=os.getenv("WHATSAPP_TOKEN"),
    server=app,  # Pass the FastAPI app instance
    verify_token=os.getenv("WHATSAPP_VERIFY_TOKEN", "change-me"),
)

@wa.on_message()
def bot_started_handler(client, message: Message):
    """Handle trigger_start trigger."""
    sender = message.from_user.wa_id
    if sender not in sessions: 
        sessions[sender] = {}

    # [NODE:2] Welcome Message
    # Show typing indicator
    time.sleep(3)
    message.reply_text(f"Hi there {message.from_user.name}")
    # [NODE:node_1767525333911] New inlinebuttons
    buttons = [
        CallbackButton(title="yes", callback_data="yes"),
        CallbackButton(title="no", callback_data="no"),
    ]
    message.reply_text("Choose an option:", buttons=buttons)

# Grouped handler for node node_1767525333911 buttons: no, yes
@wa.on_callback_button(filters.matches("no", "yes"))
def handle_callbacks_node_1767525333911(client, clb: CallbackButton):
    sender = clb.from_user.wa_id
    if sender not in sessions: 
        sessions[sender] = {}

    if clb.data == "no":
        # [NODE:node_1767526623597] no
        # Show typing indicator
        time.sleep(3)
        clb.reply_text(f"This is no {clb.from_user.name}")
    elif clb.data == "yes":
        # [NODE:node_1767526607644] yes
        # Show typing indicator
        time.sleep(3)
        clb.reply_text("This is yes")

# API endpoints
@app.get("/")
def root():
    return {"status": "ok", "message": "WhatsApp Bot is running"}

@app.get("/health")
def health():
    return {"status": "ok"}
