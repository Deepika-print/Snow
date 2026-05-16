from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from agent import run_agent
from dotenv import load_dotenv
import os
import threading

load_dotenv()

app = Flask(__name__)

ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")

client = Client(ACCOUNT_SID, AUTH_TOKEN)

# Store steps per user for live updates
user_steps = {}


def send_whatsapp(to: str, message: str):
    """Send a WhatsApp message to a number."""
    try:
        client.messages.create(
            from_=f"whatsapp:{WHATSAPP_NUMBER}",
            to=f"whatsapp:{to}",
            body=message[:1500]  # WhatsApp limit
        )
    except Exception as e:
        print(f"Send error: {e}")


def run_agent_async(task: str, user_number: str):
    """Run Snow agent and send updates back to WhatsApp."""
    steps = []

    def on_step(step_type, content):
        if step_type == "tool_call":
            steps.append(f"⚙️ {content[:100]}")
            # Send live tool update
            send_whatsapp(user_number, f"⚙️ Working: {content[:100]}")

    # Send thinking message
    send_whatsapp(user_number, "❄️ Snow is working on your task...")

    # Run the agent
    result = run_agent(task, on_step=on_step)

    # Send final answer
    send_whatsapp(user_number, f"✅ Done!\n\n{result[:1400]}")


@app.route("/whatsapp", methods=["POST"])
def whatsapp_webhook():
    """Handle incoming WhatsApp messages."""
    incoming_msg = request.values.get("Body", "").strip()
    from_number = request.values.get("From", "").replace("whatsapp:", "")

    resp = MessagingResponse()

    if not incoming_msg:
        resp.message("Send me any task and I'll complete it autonomously!")
        return str(resp)

    # Handle help command
    if incoming_msg.lower() in ("hi", "hello", "help", "/help"):
        resp.message(
            "❄️ *Snow — Autonomous AI Agent*\n\n"
            "I can help you with:\n"
            "🔍 Web search & research\n"
            "💻 Run Python code\n"
            "📁 Read & write files\n"
            "🌐 Scrape websites\n\n"
            "Just send me any task!"
        )
        return str(resp)

    # Acknowledge immediately (WhatsApp needs fast response)
    resp.message("❄️ Snow received your task. Working on it...")

    # Run agent in background thread
    thread = threading.Thread(
        target=run_agent_async,
        args=(incoming_msg, from_number),
        daemon=True
    )
    thread.start()

    return str(resp)


@app.route("/", methods=["GET"])
def home():
    return "❄️ Snow WhatsApp Bot is running!"


if __name__ == "__main__":
    print("❄️ Snow WhatsApp Bot starting...")
    print("Make sure ngrok is running: ngrok http 5000")
    app.run(port=5000, debug=False) 
