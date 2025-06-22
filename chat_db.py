import sqlite3
from datetime import datetime

DB_PATH = 'chat_app.db'

class ChatDB:
    @staticmethod
    def init():
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS ChatMessages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                meetingId TEXT NOT NULL,
                sender TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

    @staticmethod
    def save_message(meetingId, sender, message):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            INSERT INTO ChatMessages (meetingId, sender, message)
            VALUES (?, ?, ?)
        ''', (meetingId, sender, message))
        conn.commit()
        conn.close()

    @staticmethod
    def get_messages(meetingId):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            SELECT sender, message, timestamp FROM ChatMessages
            WHERE meetingId = ?
            ORDER BY timestamp ASC
        ''', (meetingId,))
        messages = c.fetchall()
        conn.close()
        return messages
if __name__ == '__main__':
    ChatDB.init()