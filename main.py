import os
from fastapi import FastAPI, Form, Response
from twilio.twiml.messaging_response import MessagingResponse
from langchain.agents import create_agent
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

# Define tools for the agent (add your custom tools here)
def get_current_time() -> str:
    """Get the current date and time."""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def calculate(expression: str) -> str:
    """Evaluate a math expression. Example: '2 + 2' or '10 * 5'"""
    try:
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"Error: {e}"

# Create the agent (LangChain v1 style)
agent = create_agent(
    model="gpt-4o-mini",
    tools=[get_current_time, calculate],
    system_prompt="You are a helpful WhatsApp assistant. Be concise and friendly.",
)

# Simple in-memory conversation history per user
conversations: dict[str, list] = {}

@app.post("/whatsapp")
async def whatsapp_webhook(Body: str = Form(...), From: str = Form(...)):
    """
    Twilio webhook endpoint for incoming WhatsApp messages.
    """
    # Get or create conversation for this user
    if From not in conversations:
        conversations[From] = []
    
    # Add user message to history
    conversations[From].append({"role": "user", "content": Body})
    
    # Invoke the agent
    response = agent.invoke({"messages": conversations[From]})
    
    # Get the last AI message
    ai_message = response["messages"][-1].content
    
    # Add AI response to history
    conversations[From].append({"role": "assistant", "content": ai_message})
    
    # Return TwiML response
    resp = MessagingResponse()
    resp.message(ai_message)
    
    return Response(content=str(resp), media_type="application/xml")


@app.get("/")
async def root():
    return {"status": "running"}
