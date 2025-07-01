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
            return 'OK', 200  # Возвращаем OK, даже если ошибка

        phone = data.get('customer_phone') or data.get('customer_attributes', {}).get('customer_phone')
        if not phone:
            print("⛔ No phone number found")
            return 'OK', 200  # Тоже OK

        chat_id = db.get_chat_id_by_phone(phone)
        print(f"🔍 Phone: {phone}, Chat ID: {chat_id}")

        if not chat_id:
            print("⛔ No user found")
            return 'OK', 200  # OK даже если чат не найден

        text = (
            f"📅 У вас новая запись!\n\n"
            f"🕒 Время: {data.get('time')}\n"
            f"📍 Адрес: {data.get('location_address_formatted')}\n"
            f"🧾 Услуга: {data.get('service_name')}"
        )

        response = requests.post(TELEGRAM_API, json={"chat_id": chat_id, "text": text})
        print(f"📨 Telegram response: {response.status_code}, {response.text}")

        return 'OK', 200  # Успешно

    except Exception as e:
        print("❌ Error in /webhook:", e)
        return 'OK', 200  # Даже в случае исключения — OK

    except Exception as e:
        print("❌ Error in /webhook:", e)
        return 'Internal server error', 500

if __name__ == '__main__':
    db.init_db()
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
