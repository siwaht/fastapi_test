import os
from fastapi import FastAPI
from pywa import WhatsApp, filters
from pywa.types import Message
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

print(f"Phone ID: {os.getenv('WHATSAPP_PHONE_ID')}")
print(f"Token exists: {bool(os.getenv('WHATSAPP_TOKEN'))}")
print(f"Verify token: {os.getenv('WHATSAPP_VERIFY_TOKEN', '123')}")

wa = WhatsApp(
    phone_id=os.getenv("WHATSAPP_PHONE_ID"),
    token=os.getenv("WHATSAPP_TOKEN"),
    server=app,
    verify_token=os.getenv("WHATSAPP_VERIFY_TOKEN", "123"),
)

@wa.on_message(filters.text)
def greet_handler(client: WhatsApp, msg: Message):
    """Simple greeting bot"""
    msg.react("👋")
    msg.reply_text(f"Hi {msg.from_user.name}! How are you?")

@app.get("/")
def root():
    return {"status": "ok", "message": "PyWa WhatsApp bot is running"}

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8001)))
