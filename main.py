from fastapi import FastAPI
from pywa import WhatsApp
from pywa.types import Message
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

wa = WhatsApp(
    phone_id=os.getenv("WHATSAPP_PHONE_ID"),
    token=os.getenv("WHATSAPP_TOKEN"),
    server=app,
    verify_token=os.getenv("WHATSAPP_VERIFY_TOKEN", "change-me"),
)

model = init_chat_model("openai:gpt-4o-mini", temperature=0.7)

agent = create_agent(
    model=model,
    system_prompt="You are a helpful AI assistant on WhatsApp. Keep responses concise.",
    tools=[],
)

@wa.on_message()
def handle_message(client, message: Message):
    if message.text:
        response = agent.invoke({"messages": [{"role": "user", "content": message.text}]})
        message.reply_text(response["messages"][-1].content)

@app.get("/")
def root():
    return {"status": "ok"}
