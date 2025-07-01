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
        if not data:
            return 'Invalid JSON', 400

        # Извлечение телефона
        phone = data.get('customer_phone') or data.get('customer_attributes', {}).get('customer_phone')
        if not phone:
            return 'No phone number found', 400

        # Получение chat_id по телефону
        chat_id = db.get_chat_id_by_phone(phone)
        if not chat_id:
            return 'No user found for this phone', 404

        # Формирование текста сообщения
        message_text = (
            f"📅 У вас новая запись!\n\n"
            f"🕒 Время: {data.get('time')}\n"
            f"📍 Адрес: {data.get('location_address_formatted')}\n"
            f"🧾 Услуга: {data.get('service_name')}"
        )

        # Отправка сообщения
        response = requests.post(TELEGRAM_API, json={
            "chat_id": chat_id,
            "text": message_text
        })

        if response.status_code != 200:
            return f"Telegram error: {response.text}", 500

        return 'Message sent', 200

    except Exception as e:
        print("Error in /webhook:", e)
        return 'Internal server error', 500

if __name__ == '__main__':
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
