from flask import Flask, request
import requests
import os
import db
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
            return 'OK', 200

        event_type = data.get('event')  # <-- вот тут читаем тип события
        print(f"📌 Event type: {event_type}")

        phone = data.get('customer_phone') or data.get('customer_attributes', {}).get('customer_phone')
        if not phone:
            print("⛔ No phone number found")
            return 'OK', 200

        chat_id = db.get_chat_id_by_phone(phone)

        print(f"🔍 Phone: {phone}, Chat ID: {chat_id}")

        if not chat_id:
            print("⛔ No user found")
            return 'OK', 200

        # теперь разные тексты по событию
        if event_type == "booking-created":
            text = (
                f"📅 Новая запись!\n\n"
                f"🕒 Время: {data.get('time')}\n"
                f"📍 Адрес: {data.get('location_address_formatted')}\n"
                f"🧾 Услуга: {data.get('service_name')}"
            )
        elif event_type == "booking-updated":
            text = (
                f"✏️ Запись обновлена!\n\n"
                f"🕒 Новое время: {data.get('time')}\n"
                f"🧾 Услуга: {data.get('service_name')}"
            )
        elif event_type == "booking-succeeded":
            text = (
                f"✅ Ваша запись успешно завершена!\n\n"
                f"Спасибо, что воспользовались нашими услугами!"
            )
        elif event_type == "booking-canceled":
            text = (
                f"❌ Ваша запись отменена.\n\n"
                f"Если это ошибка — свяжитесь с нами!"
            )
        elif event_type == "booking-rescheduled":
            text = (
                f"🔄 Ваша запись перенесена!\n\n"
                f"🕒 Новое время: {data.get('time')}"
            )
        else:
            text = (
                f"📢 Новое событие: {event_type}\n\n"
                f"Проверьте детали."
            )

        response = requests.post(TELEGRAM_API, json={"chat_id": chat_id, "text": text})
        print(f"📨 Telegram response: {response.status_code}, {response.text}")

        return 'OK', 200

    except Exception as e:
        print("❌ Error in /webhook:", e)
        return 'OK', 200

if __name__ == '__main__':
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
