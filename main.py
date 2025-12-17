import os
import logging
import asyncio
from dotenv import load_dotenv
from fastapi import FastAPI
from pywa_async import WhatsApp
from pywa.types import Message, CallbackButton, Button
from pywa import filters

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# WhatsApp configuration
wa = WhatsApp(
    phone_id=os.getenv("WHATSAPP_PHONE_ID"),
    token=os.getenv("WHATSAPP_TOKEN"),
    verify_token=os.getenv("VERIFY_TOKEN", "your_verify_token"), # Required for webhooks
    server=app,  # Integration with FastAPI
    webhook_endpoint="/webhook"
)

# Global dictionary for user state (Note: resets on restart)
sessions = {}

@wa.on_message()
async def start_handler(client: WhatsApp, msg: Message):
    sender = msg.from_user.wa_id
    sessions.setdefault(sender, {})
    
    await msg.reply(f"Hi there {msg.from_user.name}!")
    
    buttons = [
        Button(title="Yes", callback_data="one"),
        Button(title="No", callback_data="two"),
    ]
    await msg.reply("Choose an option:", buttons=buttons)

@wa.on_callback_button(filters.matches("two"))
async def handle_no(client: WhatsApp, btn: CallbackButton):
    sender = btn.from_user.wa_id
    
    # Interaction logic
    await btn.mark_as_read()
    await asyncio.sleep(1) # Simulated typing delay
    await btn.reply("This is second mate")
    await btn.react("😂")

# FastAPI health check
@app.get("/")
async def root():
    return {"status": "online"}
