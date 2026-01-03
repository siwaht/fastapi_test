import os
from fastapi import FastAPI
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

@app.post("/chat")
async def chat(message: str):
    try:
        agent = get_agent()
        result = await agent.ainvoke({"messages": [HumanMessage(content=message)]})
        reply = result["messages"][-1].content
        return {"response": reply}
    except Exception as e:
        return {"error": str(e), "response": "Sorry, I encountered an error processing your message."}

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

