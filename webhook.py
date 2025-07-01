from flask import Flask, request
import requests
import db
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    try:
        data = request.json
        print("✅ Webhook received:", data)

        if not data:
            print("⛔ Invalid JSON")
            return 'Invalid JSON', 400

        phone = data.get('customer_phone') or data.get('customer_attributes', {}).get('customer_phone')
        if not phone:
            print("⛔ No phone number found")
            return 'No phone number found', 400

        chat_id = db.get_chat_id_by_phone(phone)
        print(f"🔍 Phone: {phone}, Chat ID: {chat_id}")

        if not chat_id:
            print("⛔ No user found")
            return 'No user found for this phone', 404

        text = (
            f"📅 У вас новая запись!\n\n"
            f"🕒 Время: {data.get('time')}\n"
            f"📍 Адрес: {data.get('location_address_formatted')}\n"
            f"🧾 Услуга: {data.get('service_name')}"
        )

        response = requests.post(TELEGRAM_API, json={"chat_id": chat_id, "text": text})
        print(f"📨 Telegram response: {response.status_code}, {response.text}")

        if response.status_code != 200:
            return f"Telegram error: {response.text}", 500

        return 'Message sent', 200

    except Exception as e:
        print("❌ Error in /webhook:", e)
        return 'Internal server error', 500

if __name__ == '__main__':
    db.init_db()
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
