from flask import Flask, request
import db
import requests

app = Flask(__name__)
BOT_TOKEN = '7795364666:AAEyFR8p4ddUKl402Wro_qrfw4Vlmgvul2s'
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    data = request.json
    phone = data.get('customer_phone') or data.get('customer_attributes', {}).get('customer_phone')

    if not phone:
        return 'No phone number found', 400

    chat_id = db.get_chat_id_by_phone(phone)
    if chat_id:
        text = f"📅 У вас новая запись!\n\n🕒 Время: {data.get('time')}\n📍 Адрес: {data.get('location_address_formatted')}\n🧾 Услуга: {data.get('service_name')}"
        requests.post(TELEGRAM_API, json={"chat_id": chat_id, "text": text})
        return 'Message sent', 200

    return 'No user found for this phone', 404

if __name__ == '__main__':
    app.run(debug=True)
