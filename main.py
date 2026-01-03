import os
from fastapi import FastAPI, Form, Response
from twilio.twiml.messaging_response import MessagingResponse
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Initialize the LangChain LLM
llm = ChatOpenAI(model="gpt-4o") # Using 4o for better reasoning

@app.post("/whatsapp")
async def whatsapp_reply(Body: str = Form(...), From: str = Form(...)):
    """
    Twilio sends data as Form parameters. 
    'Body' is the message text, 'From' is the sender's WhatsApp number.
    """
    
    # 1. Process the incoming message with LangChain
    # In a real app, you'd use 'From' to look up user memory/history
    response = await llm.ainvoke([HumanMessage(content=Body)])
    ai_text = response.content

    # 2. Build the Twilio XML response (TwiML)
    twilio_resp = MessagingResponse()
    twilio_resp.message(ai_text)

    # 3. Return as XML with the correct header
    return Response(
        content=str(twilio_resp), 
        media_type="application/xml"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
