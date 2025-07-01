import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

pool = None

async def init_db():
    global pool
    pool = await asyncpg.create_pool(DATABASE_URL)
    async with pool.acquire() as conn:
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                phone TEXT UNIQUE NOT NULL,
                chat_id BIGINT NOT NULL
            )
        ''')

async def save_user(phone, chat_id):
    async with pool.acquire() as conn:
        await conn.execute('''
            INSERT INTO users (phone, chat_id)
            VALUES ($1, $2)
            ON CONFLICT (phone)
            DO UPDATE SET chat_id = EXCLUDED.chat_id
        ''', phone, chat_id)

async def get_chat_id_by_phone(phone):
    async with pool.acquire() as conn:
        result = await conn.fetchrow('SELECT chat_id FROM users WHERE phone = $1', phone)
        return result['chat_id'] if result else None
