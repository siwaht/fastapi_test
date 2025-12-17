import os
import logging
import asyncio
from fastapi import FastAPI, Request, Response
from pywa import WhatsApp
from pywa.types import Message, CallbackButton

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
        CallbackButton(title="Yes", callback_data="one"),
        CallbackButton(title="No", callback_data="two"),
    ]
    await msg.reply("Choose an option:", buttons=buttons)

@wa.on_callback_button(lambda _, btn: btn.data == "two")
async def handle_no(client: WhatsApp, btn: CallbackButton):
    sender = btn.from_user.wa_id
    
    # Interaction logic
    await btn.mark_as_read()
    await asyncio.sleep(1) # Simulated typing delay
    await btn.reply("This is second mate")
    await client.send_reaction(message_id=btn.id, emoji="😂")

# FastAPI health check
@app.get("/")
async def root():
    return {"status": "online"}