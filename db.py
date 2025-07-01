import sqlite3

DB_NAME = 'users.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT UNIQUE,
            chat_id TEXT
        )
    ''')
    conn.commit()
    conn.close()

def get_chat_id_by_phone(phone):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT chat_id FROM users WHERE phone = ?', (phone,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def save_user(phone, chat_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('INSERT OR REPLACE INTO users (phone, chat_id) VALUES (?, ?)', (phone, chat_id))
    conn.commit()
    conn.close()
