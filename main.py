import os
from fastapi import FastAPI, Form, Response
from twilio.twiml.messaging_response import MessagingResponse
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

# Initialize the LLM
llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=os.getenv("OPENAI_API_KEY")
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
        conversations[From] = [
            {"role": "system", "content": "You are a helpful WhatsApp assistant. Be concise and friendly."}
        ]
    
    # Add user message to history
    conversations[From].append({"role": "user", "content": Body})
    
    # Call the model
    response = llm.invoke(conversations[From])
    
    # Add AI response to history
    conversations[From].append({"role": "assistant", "content": response.content})
    
    # Return TwiML response
    resp = MessagingResponse()
    resp.message(response.content)
    
    return Response(content=str(resp), media_type="application/xml")


@app.get("/")
async def root():
    return {"status": "running", "message": "WhatsApp Bot is active!"}
