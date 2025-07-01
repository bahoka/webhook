import sqlite3

DB_NAME = 'users.db'

def get_chat_id_by_phone(phone):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT chat_id FROM users WHERE phone = ?', (phone,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None
