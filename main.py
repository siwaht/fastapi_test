# main.py - PyWA + LangChain Agent with FastAPI

import os
from fastapi import FastAPI
from pywa import WhatsApp
from pywa.types import Message
from langchain.agents import create_agent
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# ============ CREDENTIALS ============
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
WHATSAPP_PHONE_ID = os.getenv("WHATSAPP_PHONE_ID")
WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ============ FASTAPI APP ============
app = FastAPI()

# ============ WHATSAPP CLIENT ============
wa = WhatsApp(
    phone_id=WHATSAPP_PHONE_ID,
    token=WHATSAPP_TOKEN,
    server=app,
    verify_token=WHATSAPP_VERIFY_TOKEN,
    callback_url="https://your-domain.com/webhook",  # Replace with your webhook URL
)


# ============ LANGCHAIN AGENT TOOLS ============
def get_current_time() -> str:
    """Get the current date and time."""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def calculate(expression: str) -> str:
    """Evaluate a mathematical expression. Example: '2 + 2' or '10 * 5'"""
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"


def search_info(query: str) -> str:
    """Search for information (placeholder - replace with real search)."""
    return f"Here's information about '{query}': This is a placeholder response."


# ============ CREATE LANGCHAIN AGENT ============
agent = create_agent(
    model="openai:gpt-4o-mini",
    tools=[get_current_time, calculate, search_info],
    system_prompt="""You are a helpful WhatsApp assistant. 
    Be concise and friendly in your responses.
    Use the available tools when needed to help users.""",
)

# ============ CONVERSATION HISTORY (In-memory, use DB for production) ============
conversation_history: dict[str, list] = {}


# ============ WHATSAPP MESSAGE HANDLER ============
@wa.on_message()
def handle_message(client: WhatsApp, message: Message):
    """Handle incoming WhatsApp messages."""
    user_id = message.from_user.wa_id
    user_message = message.text

    # Initialize conversation history for new users
    if user_id not in conversation_history:
        conversation_history[user_id] = []

    # Add user message to history
    conversation_history[user_id].append({"role": "user", "content": user_message})

    try:
        # Invoke the LangChain agent
        response = agent.invoke({"messages": conversation_history[user_id]})

        # Extract assistant response
        assistant_message = response["messages"][-1].content

        # Add assistant response to history
        conversation_history[user_id].append(
            {"role": "assistant", "content": assistant_message}
        )

        # Keep only last 20 messages to prevent memory overflow
        if len(conversation_history[user_id]) > 20:
            conversation_history[user_id] = conversation_history[user_id][-20:]

        # Send response back to user
        message.reply_text(text=assistant_message)

    except Exception as e:
        message.reply_text(text=f"Sorry, an error occurred: {str(e)}")


# ============ HEALTH CHECK ENDPOINT ============
@app.get("/")
async def health_check():
    return {"status": "ok", "message": "WhatsApp LangChain Bot is running"}


# ============ RUN THE APP ============
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
