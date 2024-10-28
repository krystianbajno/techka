import sqlite3

class DataDisplay:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def display_channels(self):
        """Display all channels, groups, and supergroups with type, member counts, and user counts."""
        conn = sqlite3.connect(self.db_manager.db_name)
        cursor = conn.cursor()

        # Join channels with user_channels to get a count of unique users per channel
        cursor.execute('''
            SELECT ch.channel_id, ch.title, ch.username, ch.type, ch.member_count, COUNT(DISTINCT uc.user_id) AS user_count
            FROM channels ch
            LEFT JOIN user_channels uc ON ch.channel_id = uc.channel_id
            GROUP BY ch.channel_id
        ''')
        
        channels = cursor.fetchall()
        conn.close()

        # Display results, including user count and channel_id
        for channel_id, title, username, channel_type, member_count, user_count in channels:
            print(f"ID: {channel_id}, Title: {title}, Username: {username}, "
                  f"Type: {channel_type}, Members/Subscribers: {member_count}, Users: {user_count}")
        
        return channels
    
    def display_single_channel(self, channel_name):
        """Display information for a single channel by its title."""
        conn = sqlite3.connect(self.db_manager.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT title, username, type, member_count
            FROM channels
            WHERE title = ?
        ''', (channel_name,))
        
        channel = cursor.fetchone()
        conn.close()

        if channel:
            title, username, channel_type, member_count = channel
            print(f"Title: {title}, Username: {username}, Type: {channel_type}, Members: {member_count}")
            return channel
        else:
            print(f"No channel found with title '{channel_name}'.")
            return None
            
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
        """Display all messages in a specific channel, including user details and message dates."""
        conn = sqlite3.connect(self.db_manager.db_name)
        cursor = conn.cursor()
        
        # Fetch messages joined with user data for a specific channel based on the title
        cursor.execute('''
            SELECT messages.content, messages.date, users.username, users.first_name, users.last_name
            FROM messages
            JOIN users ON messages.user_id = users.user_id
            WHERE messages.channel_id = (SELECT channel_id FROM channels WHERE title = ?)
        ''', (channel_name,))
        
        messages = cursor.fetchall()
        conn.close()
        
        for content, date, username, first_name, last_name in messages:
            print(f"Date: {date}, User: {username}, Name: {first_name} {last_name}, Message: {content}")
            
        return messages
    
    def display_all_messages(self):
        """Display all messages, including user details and message dates."""
        conn = sqlite3.connect(self.db_manager.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT messages.content, messages.date, users.username, users.first_name, users.last_name
            FROM messages
            JOIN users ON messages.user_id = users.user_id
        ''')
        messages = cursor.fetchall()
        
        conn.close()
        
        for content, date, username, first_name, last_name in messages:
            print(f"Date: {date}, User: {username}, Name: {first_name} {last_name}, Message: {content}")
        
        return messages

    def display_messages_from_user(self, user_id):
        """Display all messages from a specific user across all channels, including message dates."""
        conn = sqlite3.connect(self.db_manager.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT content, date
            FROM messages
            WHERE user_id = ?
        ''', (user_id,))
        messages = cursor.fetchall()
        conn.close()
        
        for content, date in messages:
            print(f"Message: {content}, Date: {date}")
        
        return messages
    
    def display_latest_messages_in_channel(self, channel_name, limit=10):
        """Retrieve and display the latest messages from a specified channel, including dates."""
        conn = sqlite3.connect(self.db_manager.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT content, date 
            FROM messages 
            JOIN users ON messages.user_id = users.user_id
            WHERE channel_id = (SELECT channel_id FROM channels WHERE title = ?)
            ORDER BY date DESC
            LIMIT ?
        ''', (channel_name, limit))
        
        messages = cursor.fetchall()
        conn.close()
        
        for content, date, username, first_name, last_name in messages:
            print(f"Date: {date}, User: {username}, Name: {first_name} {last_name}, Message: {content}")
        
        return messages
    
    def display_messages_from_user_in_channel(self, user_id, channel_name):
        """Retrieve messages from a specific user within a specific channel, including dates."""
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
        
        for content, date in messages:
            print(f"Message: {content}, Date: {date}")
        
        return messages
    
    def display_channels_for_user(self, user_id):
        """Retrieve all channels a specific user has participated in."""
        conn = sqlite3.connect(self.db_manager.db_name)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT DISTINCT channels.channel_id, channels.title, channels.date_created
            FROM channels
            JOIN user_channels ON channels.channel_id = user_channels.channel_id
            WHERE user_channels.user_id = ?
        ''', (user_id,))

        channels = cursor.fetchall()
        conn.close()
        
        for channel_id, title, date_created in channels:
            print(f"Channel ID: {channel_id}, Title: {title}, Created on: {date_created}")
        
        return channels
    
    def display_users_in_channel(self, channel_name):
        """Retrieve users in a specific channel using channel_id."""
        conn = sqlite3.connect(self.db_manager.db_name)
        cursor = conn.cursor()

        # First, find the channel_id for the given channel title
        cursor.execute('SELECT channel_id FROM channels WHERE username = ? OR title = ?', (channel_name, channel_name))
        channel = cursor.fetchone()

        if channel is None:
            print(f"No channel found with title '{channel_name}'.")
            conn.close()
            return []

        channel_id = channel[0]

        cursor.execute('''
            SELECT users.user_id, users.username, users.first_name, users.last_name
            FROM users
            JOIN user_channels ON users.user_id = user_channels.user_id
            WHERE user_channels.channel_id = ?
        ''', (channel_id,))

        users = cursor.fetchall()
        
        conn.close()
        
        for user_id, username, first_name, last_name in users:
            print(f"User ID: {user_id}, Username: {username}, Name: {first_name} {last_name}")
        
        return users
    
    def display_channel_statistics(self):
        """Display subscriber counts for all collected channels."""
        conn = sqlite3.connect(self.db_manager.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT title, member_count
            FROM channels
        ''')
        channel_stats = cursor.fetchall()
        conn.close()
        
        for title, count in channel_stats:
            print(f"Channel: {title}, Subscribers: {count}")
        
        return channel_stats
