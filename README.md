# WhatsApp PyWa Bot

Simple WhatsApp greeting bot using PyWa and FastAPI.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure `.env` with your WhatsApp credentials (already done)

## Local Testing

1. Run the server:
```bash
python main.py
```

2. In another terminal, expose with ngrok:
```bash
ngrok http 8001
```

3. Copy the ngrok HTTPS URL (e.g., `https://abc123.ngrok-free.app`)

4. Configure Meta webhook:
   - Go to Meta Developer Console > Your App > WhatsApp > Configuration
   - Callback URL: `https://abc123.ngrok-free.app/`
   - Verify Token: `123`
   - Subscribe to: `messages`

5. Send a WhatsApp message to your test number

## Railway Deployment

1. Push to GitHub (already done)

2. In Railway:
   - Create new project from GitHub repo
   - Add environment variables:
     - `WHATSAPP_PHONE_ID`
     - `WHATSAPP_TOKEN`
     - `WHATSAPP_VERIFY_TOKEN`
   - Railway will auto-deploy

3. Configure Meta webhook with Railway URL (e.g., `https://yourapp.railway.app/`)

## Troubleshooting

**Bot not responding:**
- Check Railway logs for errors
- Verify webhook is configured correctly in Meta console
- Ensure verify token matches in both .env and Meta console
- Check that `messages` subscription is active

**Local testing fails:**
- Install pywa: `pip install pywa`
- Check .env file exists and has correct values
- Verify ngrok is running and URL is updated in Meta console

## API Endpoints

- `GET /` - Health check
- `GET /health` - Health status
- `POST /webhooks/whatsapp` - WhatsApp webhook (auto-created by PyWa)
