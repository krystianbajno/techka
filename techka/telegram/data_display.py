import sqlite3

class DataDisplay:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def display_channels(self):
        """Display all channels in the database."""
        conn = sqlite3.connect(self.db_manager.db_name)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM channels')
        channels = cursor.fetchall()
        conn.close()
        for channel in channels:
            print(channel)
        
        return channels
            
    def display_all_users(self):
        """Retrieve and display all unique users across all channels."""
        conn = sqlite3.connect(self.db_manager.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT DISTINCT user_id, username, first_name, last_name
            FROM users
        ''')
        
        users = cursor.fetchall()
        conn.close()
        
        for user in users:
            print(user)
            
        return users

    def display_messages_in_channel(self, channel_name):
        """Display all messages in a specific channel."""
        conn = sqlite3.connect(self.db_manager.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT content, date FROM messages
            WHERE channel_id = (SELECT channel_id FROM channels WHERE title = ?)
        ''', (channel_name,))
        messages = cursor.fetchall()
        conn.close()
        for message in messages:
            print(message)
            
        return messages

    def display_messages_from_user(self, user_id):
        """Display all messages from a specific user across all channels."""
        conn = sqlite3.connect(self.db_manager.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT content, date FROM messages
            WHERE user_id = ?
        ''', (user_id,))
        messages = cursor.fetchall()
        conn.close()
        for message in messages:
            print(message)
        
        return messages
    
    def display_latest_messages_in_channel(self, channel_name, limit=10):
        """Retrieve and display the latest messages from a specified channel."""
        conn = sqlite3.connect(self.db_manager.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT content, date 
            FROM messages 
            WHERE channel_id = (SELECT channel_id FROM channels WHERE title = ?)
            ORDER BY date DESC
            LIMIT ?
        ''', (channel_name, limit))
        
        messages = cursor.fetchall()
        conn.close()
        return messages
    
    def display_messages_from_user_in_channel(self, user_id, channel_name):
        """Retrieve messages from a specific user within a specific channel."""
        conn = sqlite3.connect(self.db_manager.db_name)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT content, date
            FROM messages
            WHERE user_id = ? AND channel_id = (SELECT channel_id FROM channels WHERE title = ?)
            ORDER BY date DESC
        ''', (user_id, channel_name))

        messages = cursor.fetchall()
        conn.close()
        return messages
    
    def display_channels_for_user(self, user_id):
        """Retrieve all channels a specific user has participated in."""
        conn = sqlite3.connect(self.db_manager.db_name)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT DISTINCT channels.title 
            FROM channels
            JOIN user_channels ON channels.channel_id = user_channels.channel_id
            WHERE user_channels.user_id = ?
        ''', (user_id,))

        channels = cursor.fetchall()
        conn.close()
        return channels
    
    
    def display_users_in_channel(self, channel_name):
        """Retrieve users in a specific channel."""
        conn = sqlite3.connect(self.db_manager.db_name)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT users.user_id, users.username, users.first_name, users.last_name
            FROM users
            JOIN user_channels ON users.user_id = user_channels.user_id
            JOIN channels ON user_channels.channel_id = channels.channel_id
            WHERE channels.title = ?
        ''', (channel_name,))

        users = cursor.fetchall()
        conn.close()
        return users