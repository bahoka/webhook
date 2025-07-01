import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# создаем подключение
conn = psycopg2.connect(DATABASE_URL)
conn.autocommit = True

def init_db():
    with conn.cursor() as cur:
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                phone TEXT UNIQUE NOT NULL,
                chat_id BIGINT NOT NULL
            )
        ''')

def save_user(phone, chat_id):
    with conn.cursor() as cur:
        cur.execute('''
            INSERT INTO users (phone, chat_id)
            VALUES (%s, %s)
            ON CONFLICT (phone)
            DO UPDATE SET chat_id = EXCLUDED.chat_id
        ''', (phone, chat_id))

def get_chat_id_by_phone(phone):
    with conn.cursor() as cur:
        cur.execute('SELECT chat_id FROM users WHERE phone = %s', (phone,))
        result = cur.fetchone()
        return result[0] if result else None
