import os
from fastapi import FastAPI, Form, Response
from twilio.twiml.messaging_response import MessagingResponse
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Validate required environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is not set. Please set it in Railway environment variables.")

# Initialize the LangChain LLM
# ChatOpenAI automatically reads OPENAI_API_KEY from environment variables
llm = ChatOpenAI(model="gpt-4o")

@app.get("/")
async def root():
    """Health check endpoint for Railway"""
    return {"status": "ok", "message": "FastAPI WhatsApp bot is running"}

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.post("/whatsapp")
async def whatsapp_reply(Body: str = Form(...), From: str = Form(...)):
    """
    Twilio sends data as Form parameters. 
    'Body' is the message text, 'From' is the sender's WhatsApp number.
    """
    try:
        # 1. Process the incoming message with LangChain
        # In a real app, you'd use 'From' to look up user memory/history
        response = await llm.ainvoke([HumanMessage(content=Body)])
        ai_text = response.content

        # 2. Build the Twilio XML response (TwiML)
        twilio_resp = MessagingResponse()
        twilio_resp.message(ai_text)

        # 3. Return as XML with the correct header (text/xml per Twilio docs)
        return Response(
            content=str(twilio_resp),
            media_type="text/xml"
        )
    except Exception as e:
        # Log error and return a safe TwiML response
        print(f"Error processing message: {str(e)}")
        twilio_resp = MessagingResponse()
        twilio_resp.message("Sorry, I encountered an error processing your message. Please try again.")
        return Response(
            content=str(twilio_resp),
            media_type="text/xml"
        )

if __name__ == "__main__":
    import uvicorn
    # Railway provides PORT via environment variable, default to 8000 for local dev
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
