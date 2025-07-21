import sqlite3

conn = sqlite3.connect('banned_users.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS banned_users (
    user_id TEXT PRIMARY KEY,
    reason TEXT,
    banned_by TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')

conn.commit()
conn.close()
