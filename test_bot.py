import os
from dotenv import load_dotenv

load_dotenv()

print("=== Environment Variables Check ===")
print(f"WHATSAPP_PHONE_ID: {os.getenv('WHATSAPP_PHONE_ID')}")
print(f"WHATSAPP_TOKEN (first 20 chars): {os.getenv('WHATSAPP_TOKEN', '')[:20]}...")
print(f"WHATSAPP_VERIFY_TOKEN: {os.getenv('WHATSAPP_VERIFY_TOKEN')}")
print(f"WHATSAPP_BUSINESS_ID: {os.getenv('WHATSAPP_BUSINESS_ID')}")

print("\n=== Testing PyWa Import ===")
try:
    from pywa import WhatsApp
    print("✓ PyWa imported successfully")
    
    print("\n=== Creating WhatsApp client ===")
    wa = WhatsApp(
        phone_id=os.getenv("WHATSAPP_PHONE_ID"),
        token=os.getenv("WHATSAPP_TOKEN"),
        verify_token=os.getenv("WHATSAPP_VERIFY_TOKEN", "123"),
    )
    print("✓ WhatsApp client created successfully")
    print(f"Phone ID: {wa.phone_id}")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
