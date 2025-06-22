import sqlite3

DB_PATH = "meetings.db"

# ----------------- User Table ----------------- #
class UserDB:
    @staticmethod
    def init(cursor):
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS User (
                userId TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')

    @staticmethod
    def add_user(user_id, name, email, password):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        try:
            c.execute('INSERT INTO User (userId, name, email, password) VALUES (?, ?, ?, ?)',
                      (user_id, name, email, password))
            conn.commit()
        except sqlite3.IntegrityError as e:
            print("User insertion error:", e)
        conn.close()

    @staticmethod
    def get_all_users():
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM User")
        rows = c.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    @staticmethod
    def user_exists(user_id):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT 1 FROM User WHERE userId = ?', (user_id,))
        result = c.fetchone()
        conn.close()
        return result is not None
    @staticmethod
    def get_password(user_id):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT password FROM User WHERE userId = ?', (user_id,))
        result = c.fetchone()
        conn.close()
        return result[0] if result else None



# ----------------- Meeting Table ----------------- #
class MeetingDB:
    @staticmethod
    def init(cursor):
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS meetings (
                meeting_id TEXT PRIMARY KEY,
                passkey TEXT NOT NULL,
                host TEXT,
                co_host TEXT,
                meetingTitle TEXT
            )
        ''')

    @staticmethod
    def add_meeting(meeting_id, passkey, host=None, co_host=None, meeting_title=None):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        try:
            c.execute('''
                INSERT INTO meetings (meeting_id, passkey, host, co_host, meetingTitle)
                VALUES (?, ?, ?, ?, ?)
            ''', (meeting_id, passkey, host, co_host, meeting_title))
            conn.commit()
        except sqlite3.IntegrityError as e:
            print("Meeting insertion error:", e)
        conn.close()

    @staticmethod
    def meeting_exists(meeting_id):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT 1 FROM meetings WHERE meeting_id = ?', (meeting_id,))
        result = c.fetchone()
        conn.close()
        return result is not None

    @staticmethod
    def get_passkey(meeting_id):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT passkey FROM meetings WHERE meeting_id = ?', (meeting_id,))
        result = c.fetchone()
        conn.close()
        return result[0] if result else None

    @staticmethod
    def get_host(meeting_id):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT host FROM meetings WHERE meeting_id = ?', (meeting_id,))
        result = c.fetchone()
        conn.close()
        return result[0] if result else None

    @staticmethod
    def update_host(meeting_id, new_host):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('UPDATE meetings SET host = ? WHERE meeting_id = ?', (new_host, meeting_id))
        conn.commit()
        conn.close()

    @staticmethod
    def update_co_host(meeting_id, new_co_host):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('UPDATE meetings SET co_host = ? WHERE meeting_id = ?', (new_co_host, meeting_id))
        conn.commit()
        conn.close()

    @staticmethod
    def delete_meeting(meeting_id):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('DELETE FROM meetings WHERE meeting_id = ?', (meeting_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def get_meeting_title(meeting_id):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT meetingTitle FROM meetings WHERE meeting_id = ?', (meeting_id,))
        result = c.fetchone()
        conn.close()
        return result[0] if result else None

    @staticmethod
    def update_meeting_title(meeting_id, new_title):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('UPDATE meetings SET meetingTitle = ? WHERE meeting_id = ?', (new_title, meeting_id))
        conn.commit()
        conn.close()


# ----------------- UserMeeting Table ----------------- #
class UserMeetingDB:
    @staticmethod
    def init(cursor):
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS userMeetings (
                userId TEXT NOT NULL,
                meetingId TEXT NOT NULL,
                isLive INTEGER DEFAULT 1,
                isBlocked INTEGER DEFAULT 0,
                difi_sharekey TEXT,
                private_key TEXT,
                public_key TEXT,
                FOREIGN KEY (userId) REFERENCES User(userId),
                FOREIGN KEY (meetingId) REFERENCES meetings(meeting_id)
            )
        ''')

    @staticmethod
    def add_user_to_meeting(user_id, meeting_id, isLive=1, isBlocked=0, difi_sharekey=None, private_key=None, public_key=None):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        # Check if this user-meeting pair already exists
        c.execute('''
            SELECT 1 FROM userMeetings WHERE userId = ? AND meetingId = ?
        ''', (user_id, meeting_id))
        if c.fetchone():
            conn.close()
            return -1  # Already exists

        try:
            c.execute('''
                INSERT INTO userMeetings (userId, meetingId, isLive, isBlocked, difi_sharekey, private_key, public_key)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, meeting_id, isLive, isBlocked, difi_sharekey, private_key, public_key))
            conn.commit()
        except sqlite3.IntegrityError as e:
            print("UserMeeting insertion error:", e)
        finally:
            conn.close()

    @staticmethod
    def get_blocked_users(meeting_id):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT userId FROM userMeetings WHERE meetingId = ? AND isBlocked = 1', (meeting_id,))
        result = c.fetchall()
        conn.close()
        return [row[0] for row in result]
    @staticmethod
    def get_meetings_for_user(user_id):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT meetingId FROM userMeetings WHERE userId = ?', (user_id,))
        result = c.fetchall()
        conn.close()
        return [row[0] for row in result]

    @staticmethod
    def get_users_for_meeting(meeting_id):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT userId FROM userMeetings WHERE meetingId = ?', (meeting_id,))
        result = c.fetchall()
        conn.close()
        return [row[0] for row in result]

    @staticmethod
    def get_is_blocked(user_id, meeting_id):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT isBlocked FROM userMeetings WHERE userId = ? AND meetingId = ?', (user_id, meeting_id))
        result = c.fetchone()
        conn.close()
        return result[0] if result else None

    @staticmethod
    def get_attribute(user_id, meeting_id, column_name):
        allowed = ['private_key', 'public_key', 'difi_sharekey', 'isLive']
        if column_name not in allowed:
            raise ValueError(f"Invalid column: {column_name}")
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(f'SELECT {column_name} FROM userMeetings WHERE userId = ? AND meetingId = ?', (user_id, meeting_id))
        result = c.fetchone()
        conn.close()
        return result[0] if result else None
    @staticmethod
    def update_user_block_status(user_id, meeting_id, isBlocked, difi_sharekey):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            UPDATE userMeetings
            SET isBlocked = ?, difi_sharekey = ?
            WHERE userId = ? AND meetingId = ?
        ''', (isBlocked, difi_sharekey, user_id, meeting_id))
        conn.commit()
        conn.close()


# ----------------- Init Function ----------------- #
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    UserDB.init(c)
    MeetingDB.init(c)
    UserMeetingDB.init(c)
    conn.commit()
    conn.close()



if __name__ == '__main__':
    init_db()