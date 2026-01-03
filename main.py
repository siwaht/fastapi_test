import os
import logging
from fastapi import FastAPI
from pywa import WhatsApp, filters
from pywa.types import Message
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
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

# Initialize LangChain agent
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
agent = create_agent(llm, tools=[], system_prompt="You are a helpful WhatsApp assistant.")

# Initialize WhatsApp client
wa = WhatsApp(
    phone_id=phone_id,
    token=token,
    server=app,
    verify_token=verify_token,
    app_secret=app_secret,
    validate_updates=bool(app_secret),
)

@wa.on_raw_update()
def raw_update_handler(client: WhatsApp, update: dict):
    """Debug: log all incoming updates"""
    logger.info(f"Raw update received: {update}")

@wa.on_message(filters.text)
def agent_handler(client: WhatsApp, msg: Message):
    """LangChain AI agent handler"""
    logger.info(f"Received message from {msg.from_user.name}: {msg.text}")
    try:
        # Get response from LangChain agent
        result = agent.invoke({"messages": [HumanMessage(content=msg.text)]})
        reply = result["messages"][-1].content
        
        # Send reply via WhatsApp
        msg.reply_text(reply)
        logger.info(f"Sent AI reply to {msg.from_user.name}")
    except Exception as e:
        logger.error(f"Error handling message: {e}")
        msg.reply_text("Sorry, I encountered an error. Please try again.")

@app.get("/")
def root():
    return {"status": "ok", "message": "PyWa WhatsApp bot is running"}

@app.get("/health")
def health():
    return {"status": "ok"}

