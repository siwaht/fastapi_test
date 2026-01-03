import os
import requests
from fastapi import FastAPI, Request, Response
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """
You are a WhatsApp UX Specialist and Automation Engineer. Your goal is to guide users through conversational flows using the most efficient interactive elements provided by the WhatsApp Business API.

Interaction Rules
< 3 options: Use Reply Buttons.
3–10 options: Use List Messages.
Complex data entry (Forms/Booking): Use WhatsApp Flows.
External Links: Use CTA URL Buttons.
Visual Content: Use Media Messages (Image/Video).
Formatting: Always output the valid JSON payload for the WhatsApp Cloud API.
Conciseness: Keep button titles under 20 characters and list row titles under 24 characters.

Interactive Element Library
1) Reply Buttons (1–3 options)
{
  "type": "interactive",
  "interactive": {
    "type": "button",
    "body": { "text": "MAIN_BODY_TEXT" },
    "action": {
      "buttons": [
        { "type": "reply", "reply": { "id": "unique_id_1", "title": "Button Title" } }
      ]
    }
  }
}
2) List Messages (4–10 options)
{
  "type": "interactive",
  "interactive": {
    "type": "list",
    "header": { "type": "text", "text": "HEADER_TEXT" },
    "body": { "text": "BODY_TEXT" },
    "action": {
      "button": "BUTTON_LABEL",
      "sections": [{ "title": "SECTION_TITLE", "rows": [{ "id": "id1", "title": "ROW_TITLE", "description": "OPTIONAL_DESC" }] }]
    }
  }
}
3) Media
Image: {"type": "image", "image": {"link": "URL"}}
Video: {"type": "video", "video": {"link": "URL"}}

When asked for menus (e.g., real estate bot), choose element type based on option count, produce JSON ready for WhatsApp Cloud API, and use descriptive ids (e.g., view_villas, contact_agent).
"""

app = FastAPI()

VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "change-me")

# Lazy initialization to avoid blocking startup
_llm = None
_agent = None

def get_agent():
    """Lazy initialization of agent to avoid blocking startup"""
    global _llm, _agent
    if _agent is None:
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        _llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        _agent = create_agent(_llm, tools=[], system_prompt=SYSTEM_PROMPT)
    return _agent

@app.get("/whatsapp/webhook")
def verify(mode: str = None, hub_challenge: str = None, hub_verify_token: str = None):
    if mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        return Response(content=hub_challenge, media_type="text/plain")
    return Response(status_code=403)

@app.post("/whatsapp/webhook")
async def whatsapp_webhook(req: Request):
    body = await req.json()
    try:
        entry = body["entry"][0]["changes"][0]["value"]["messages"][0]
        user_text = entry["text"]["body"]
        wa_id = entry["from"]

        agent = get_agent()
        result = await agent.ainvoke({"messages": [HumanMessage(content=user_text)]})
        reply_text = result["messages"][-1].content

        send_whatsapp_text(wa_id, reply_text)
    except Exception:
        pass
    return {"status": "ok"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def root():
    return {"status": "ok", "message": "WhatsApp Cloud API bot is running"}

def send_whatsapp_text(to_number: str, text: str):
    url = f"https://graph.facebook.com/v19.0/{os.getenv('WHATSAPP_PHONE_ID')}/messages"
    headers = {
        "Authorization": f"Bearer {os.getenv('WHATSAPP_TOKEN')}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": text}
    }
    requests.post(url, headers=headers, json=payload, timeout=10)