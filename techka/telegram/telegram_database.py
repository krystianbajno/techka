import sqlite3

class DatabaseManager:
    def __init__(self, db_name='telegram_database.db'):
        self.db_name = db_name
        self._initialize_database()

    def _initialize_database(self):
        """ Initialize the database and create tables if they do not exist """
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS channels (
                id INTEGER PRIMARY KEY,
                channel_id INTEGER UNIQUE,
                title TEXT,
                username TEXT,
                date_created TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                user_id INTEGER UNIQUE,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                bio TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_channels (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                channel_id INTEGER,
                UNIQUE(user_id, channel_id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY,
                message_id INTEGER,
                channel_id INTEGER,
                user_id INTEGER,
                date TEXT,
                content TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attachments (
                id INTEGER PRIMARY KEY,
                message_id INTEGER,
                file_name TEXT,
                file_type TEXT,
                file_path TEXT
            )
        ''')

        conn.commit()
        conn.close()
