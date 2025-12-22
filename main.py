import os
import requests
import logging
from typing import Annotated
from typing_extensions import TypedDict
from dotenv import load_dotenv

from fastapi import FastAPI, Request, Response, Query
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

# 1. SETUP & CONFIG
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# 2. WHATSAPP SENDER TOOL
def send_whatsapp_text(recipient_id: str, message_text: str):
    """Sends a message via WhatsApp Cloud API."""
    url = f"https://graph.facebook.com/v21.0/{os.getenv('WA_PHONE_ID')}/messages"
    headers = {
        "Authorization": f"Bearer {os.getenv('WA_TOKEN')}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": recipient_id,
        "type": "text",
        "text": {"body": message_text}
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

# 3. LANGGRAPH AGENT LOGIC
class State(TypedDict):
    # add_messages ensures chat history is appended correctly
    messages: Annotated[list, add_messages]
    sender_id: str

llm = ChatOpenAI(model="gpt-4o-mini")

def chatbot_node(state: State):
    """The brain of the bot: generates a response and sends it."""
    # Call LLM to get a friendly response
    response = llm.invoke(state["messages"])
    
    # Send the response back to WhatsApp
    send_whatsapp_text(state["sender_id"], response.content)
    
    return {"messages": [response]}

# Define the Graph
workflow = StateGraph(State)
workflow.add_node("chatbot", chatbot_node)
workflow.add_edge(START, "chatbot")
workflow.add_edge("chatbot", END)

# Compile the agent
agent = workflow.compile()

# 4. FASTAPI WEBHOOK ROUTES
@app.get("/webhook")
async def verify_handshake(
    token: str = Query(..., alias="hub.verify_token"), 
    challenge: str = Query(..., alias="hub.challenge")
):
    """Verifies the webhook connection with Meta."""
    if token == os.getenv("WA_VERIFY_TOKEN"):
        return Response(content=challenge, media_type="text/plain")
    return Response(content="Invalid token", status_code=403)

@app.post("/webhook")
async def handle_incoming_message(request: Request):
    """Receives user messages and triggers the LangGraph agent."""
    data = await request.json()
    
    try:
        # Navigate Meta's JSON structure
        entry = data.get('entry', [{}])[0]
        changes = entry.get('changes', [{}])[0]
        value = changes.get('value', {})
        
        if "messages" in value:
            message = value['messages'][0]
            sender_id = message['from']
            user_name = value.get('contacts', [{}])[0].get('profile', {}).get('name', 'User')
            
            # Get text or default if it's media
            message_body = message.get('text', {}).get('body', "[Media/Other Message]")

            logger.info(f"Received message from {user_name}: {message_body}")

            # Trigger the Agent
            agent.invoke({
                "messages": [("human", message_body)],
                "sender_id": sender_id
            })

    except Exception as e:
        logger.error(f"Webhook error: {e}")

    return {"status": "success"}

@app.get("/")
async def root():
    return {"status": "online", "framework": "FastAPI + LangGraph"}