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
                type TEXT,           -- channel, group, or supergroup
                member_count INTEGER,
                date_created TEXT
            )
        ''')

        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                user_id INTEGER UNIQUE,
                username TEXT,
                first_name TEXT,
                last_name TEXT
            )
        ''')

        # User-channel association table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_channels (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                channel_id INTEGER,
                UNIQUE(user_id, channel_id)
            )
        ''')

        # Messages table
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

        # Attachments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attachments (
                id INTEGER PRIMARY KEY,
                message_id INTEGER,
                file_name TEXT,
                file_type TEXT,
                file_path TEXT,
                mime_type TEXT,
                size INTEGER
            )
        ''')

        conn.commit()
        conn.close()

    def save_user(self, user_data, channel_id):
        """
        Save user information and associate the user with a specific channel.

        Parameters:
            user_data (dict): Dictionary containing user details (user_id, username, first_name, last_name).
            channel_id (int): The ID of the channel the user belongs to.
        """
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        # Insert user data into the users table if the user does not already exist
        cursor.execute('''
            INSERT OR IGNORE INTO users (user_id, username, first_name, last_name)
            VALUES (:user_id, :username, :first_name, :last_name)
        ''', user_data)

        # Insert channel-user relationship into user_channels
        cursor.execute('''
            INSERT OR IGNORE INTO user_channels (user_id, channel_id)
            VALUES (?, ?)
        ''', (user_data['user_id'], channel_id))

        conn.commit()
        conn.close()


    def save_message(self, message_data):
        """
        Save a message to the database.

        Parameters:
            message_data (dict): Dictionary containing message details (message_id, user_id, channel_id, date, content).
        """
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO messages (message_id, user_id, channel_id, date, content)
            VALUES (:message_id, :user_id, :channel_id, :date, :content)
        ''', message_data)

        conn.commit()
        conn.close()

    def save_channel_info(self, channel_id, title, username, channel_type, member_count, date_created):
        """Save or update channel info with all relevant details."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO channels (channel_id, title, username, type, member_count, date_created)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (channel_id, title, username, channel_type, member_count, date_created))
        conn.commit()
        conn.close()