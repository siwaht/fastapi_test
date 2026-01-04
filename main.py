from pywa import WhatsApp
from pywa.types import Message, CallbackButton, CallbackSelection
import logging
import os
import asyncio

# Global dictionary to store user state
sessions = {}

# Configure logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# WhatsApp configuration
wa = WhatsApp(
    phone_id=os.getenv("WHATSAPP_PHONE_ID"),
    token=os.getenv("WHATSAPP_TOKEN"),
)

@wa.on_message()
async def bot_started_handler(client, message: Message):
    """Handle trigger_start trigger."""
    sender = message.from_user.wa_id
    if sender not in sessions: sessions[sender] = {}
    user_data = sessions[sender]

    # [NODE:2] Welcome Message
    # Show typing indicator
    await asyncio.sleep(3)
    await client.send_message(sender, f"HI there {message.from_user.name}")
    # [NODE:node_1767525333911] New inlinebuttons
    buttons = [
        CallbackButton(title="yes", callback_data="yes"),
        CallbackButton(title="no", callback_data="no"),
    ]
    await client.send_message(sender, "Choose an option:", buttons=buttons)

# Grouped handler for node node_1767525333911 buttons: no, yes
@wa.on_callback_button(matches=["no","yes"])
async def handle_callbacks_node_1767525333911(client, message: CallbackButton):
    sender = message.from_user.wa_id
    if sender not in sessions: sessions[sender] = {}
    user_data = sessions[sender]

    if message.data == "no":
        # [NODE:node_1767526623597] no
        # Show typing indicator
        await asyncio.sleep(3)
        await client.send_message(sender, f"This is no {message.from_user.name}")
    elif message.data == "yes":
        # [NODE:node_1767526607644] yes
        # Show typing indicator
        await asyncio.sleep(3)
        await client.send_message(sender, "This is yes")

# Start the WhatsApp webhook server
if __name__ == "__main__":
    wa.run(host="0.0.0.0", port=8080)