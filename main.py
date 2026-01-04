import os
import logging
from fastapi import FastAPI
from pywa import WhatsApp, filters, types
from pywa.types import Message, CallbackButton
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI()

# Environment variables
phone_id = os.getenv("WHATSAPP_PHONE_ID")
token = os.getenv("WHATSAPP_TOKEN")
verify_token = os.getenv("WHATSAPP_VERIFY_TOKEN", "change-me")
app_secret = os.getenv("WHATSAPP_APP_SECRET")

if not phone_id or not token:
    raise ValueError("WHATSAPP_PHONE_ID and WHATSAPP_TOKEN must be set")

# Initialize LangChain agent with UX specialist prompt
SYSTEM_PROMPT = """You are a WhatsApp UX Specialist and Automation Engineer. 
Guide users through conversational flows using interactive elements.
Keep responses concise and helpful."""

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
agent = create_agent(llm, tools=[], system_prompt=SYSTEM_PROMPT)

# Initialize WhatsApp client
wa = WhatsApp(
    phone_id=phone_id,
    token=token,
    server=app,
    verify_token=verify_token,
    app_secret=app_secret,
    validate_updates=bool(app_secret),
)

# === 1. REPLY BUTTONS (< 3 options) ===
@wa.on_message(filters.matches("menu", "start", ignore_case=True))
def show_menu(client: WhatsApp, msg: Message):
    """Main menu with reply buttons"""
    msg.reply_text(
        text="Welcome! How can I help you?",
        buttons=[
            types.Button(title="💬 Chat with AI", callback_data="chat_ai"),
            types.Button(title="🏠 Properties", callback_data="properties"),
        ]
    )

# === 2. LIST MESSAGE (4-10 options) ===
@wa.on_callback_button(filters.startswith("properties"))
def show_properties(client: WhatsApp, clb: CallbackButton):
    """Property list with sections"""
    clb.reply(
        text="Browse our property collection:",
        buttons=types.SectionList(
            button_title="View Properties",
            sections=[
                types.Section(
                    title="Residential",
                    rows=[
                        types.SectionRow(
                            title="Luxury Villas",
                            callback_data="view_villas",
                            description="Premium locations"
                        ),
                        types.SectionRow(
                            title="Apartments",
                            callback_data="view_apartments",
                            description="Modern living"
                        ),
                    ]
                ),
                types.Section(
                    title="Commercial",
                    rows=[
                        types.SectionRow(
                            title="Office Spaces",
                            callback_data="view_offices",
                            description="Business ready"
                        ),
                        types.SectionRow(
                            title="Retail Shops",
                            callback_data="view_retail",
                            description="High foot traffic"
                        ),
                    ]
                ),
            ]
        )
    )

# === 3. HANDLE BUTTON CALLBACKS ===
@wa.on_callback_button(filters.startswith("view_"))
def property_details(client: WhatsApp, clb: CallbackButton):
    """Show property details with action buttons"""
    property_type = clb.data.replace("view_", "").replace("_", " ").title()
    
    clb.reply_text(
        text=f"🏠 {property_type}\n\n"
             f"📍 Location: Downtown\n"
             f"💰 Starting from $500,000\n"
             f"📏 Size: 2000+ sq ft",
        buttons=[
            types.Button(title="📞 Contact Agent", callback_data="contact"),
            types.Button(title="🔙 Back", callback_data="properties"),
        ]
    )

@wa.on_callback_button(filters.matches("contact"))
def contact_agent(client: WhatsApp, clb: CallbackButton):
    """Contact confirmation"""
    clb.reply_text(
        "✅ Agent will contact you soon!\n"
        "Direct: +1-555-REAL-EST\n\n"
        "Type 'menu' to return."
    )

# === 4. SEND IMAGES ===
@wa.on_message(filters.matches("photo", "image", ignore_case=True))
def send_property_image(client: WhatsApp, msg: Message):
    """Send property image"""
    msg.reply_image(
        image="https://images.unsplash.com/photo-1564013799919-ab600027ffc6",
        caption="🏡 Modern Villa - $750,000\n\nType 'menu' for more"
    )

# === 5. AI CHAT (default handler) ===
@wa.on_callback_button(filters.matches("chat_ai"))
def enable_ai_chat(client: WhatsApp, clb: CallbackButton):
    clb.reply_text("Ask me anything! (Type 'menu' to go back)")

@wa.on_message(filters.text)
def ai_handler(client: WhatsApp, msg: Message):
    """AI agent for general queries"""
    logger.info(f"AI responding to {msg.from_user.name}")
    try:
        result = agent.invoke({"messages": [HumanMessage(content=msg.text)]})
        reply = result["messages"][-1].content
        msg.reply_text(reply)
    except Exception as e:
        logger.error(f"Error: {e}")
        msg.reply_text("Error occurred. Type 'menu' to restart.")

# === API ENDPOINTS ===
@app.get("/")
def root():
    return {"status": "ok", "message": "Interactive WhatsApp Bot"}

@app.get("/health")
def health():
    return {"status": "ok"}