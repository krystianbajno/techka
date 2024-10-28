import sqlite3
import re
from collections import defaultdict

class DataProcessor:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        
        
    def analyze_user_activity(self, channel_name):
        """Analyze user activity levels in a specified channel."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT users.username, COUNT(messages.message_id) as message_count
            FROM messages
            JOIN users ON messages.user_id = users.user_id
            WHERE messages.channel_id = (SELECT channel_id FROM channels WHERE title = ?)
            GROUP BY users.username
            ORDER BY message_count DESC
        ''', (channel_name,))
        
        activity_data = cursor.fetchall()
        conn.close()
        return activity_data
        
    def keyword_analysis_in_channel(self, keywords, channel_name):
        """Analyze messages in a specified channel for specified keywords."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        keyword_counts = {}
        for keyword in keywords:
            cursor.execute('''
                SELECT COUNT(*) 
                FROM messages
                WHERE channel_id = (SELECT channel_id FROM channels WHERE title = ?)
                AND content LIKE ?
            ''', (channel_name, f'%{keyword}%'))
            count = cursor.fetchone()[0]
            keyword_counts[keyword] = count
        
        conn.close()
        return keyword_counts

    def process_user_interactions(self, channel_name):
        """Process user interactions for posts in a specific channel."""
        conn = sqlite3.connect(self.db_manager.db_name)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT users.username, COUNT(messages.id) as post_count
            FROM messages
            JOIN users ON messages.user_id = users.user_id
            WHERE messages.channel_id = (SELECT channel_id FROM channels WHERE title = ?)
            GROUP BY users.username
            ORDER BY post_count DESC
        ''', (channel_name,))

        results = cursor.fetchall()
        conn.close()
        return results

    def analyze_keywords_in_messages(self, keywords, channel_name):
        """Analyze messages for specific keywords."""
        conn = sqlite3.connect(self.db_manager.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT content FROM messages
            WHERE channel_id = (SELECT channel_id FROM channels WHERE title = ?)
        ''', (channel_name,))

        messages = cursor.fetchall()
        keyword_count = defaultdict(int)

        for message in messages:
            for keyword in keywords:
                if re.search(r'\b' + re.escape(keyword) + r'\b', message[0], re.IGNORECASE):
                    keyword_count[keyword] += 1

        conn.close()
        return dict(keyword_count)
