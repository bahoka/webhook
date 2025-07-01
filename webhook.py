from flask import Flask, request
import requests
import os
import asyncio
import db
from dotenv import load_dotenv

# если хочешь оставить run_until_complete внутри Flask
# добавляем nest_asyncio:
import nest_asyncio
nest_asyncio.apply()

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
            return 'OK', 200

        phone = data.get('customer_phone') or data.get('customer_attributes', {}).get('customer_phone')
        if not phone:
            print("⛔ No phone number found")
            return 'OK', 200

        # теперь мы можем смело вызывать run_until_complete
        loop = asyncio.get_event_loop()
        chat_id = loop.run_until_complete(db.get_chat_id_by_phone(phone))

        print(f"🔍 Phone: {phone}, Chat ID: {chat_id}")

        if not chat_id:
            print("⛔ No user found")
            return 'OK', 200

        text = (
            f"📅 У вас новая запись!\n\n"
            f"🕒 Время: {data.get('time')}\n"
            f"📍 Адрес: {data.get('location_address_formatted')}\n"
            f"🧾 Услуга: {data.get('service_name')}"
        )

        response = requests.post(TELEGRAM_API, json={"chat_id": chat_id, "text": text})
        print(f"📨 Telegram response: {response.status_code}, {response.text}")

        return 'OK', 200

    except Exception as e:
        print("❌ Error in /webhook:", e)
        return 'OK', 200


if __name__ == '__main__':
    port = int(os.getenv("PORT", 8080))

    # инициализация базы один раз перед запуском
    asyncio.run(db.init_db())

    app.run(host="0.0.0.0", port=port)
