import sqlite3
import re
from collections import defaultdict

class DataIndexer:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def index_all_data(self):
        """Index messages, users, channels, and attachments for fast searching."""
        conn = sqlite3.connect(self.db_manager.db_name)
        cursor = conn.cursor()

        cursor.execute('SELECT message_id, content FROM messages')
        messages = cursor.fetchall()
        cursor.execute('SELECT user_id, username FROM users')
        users = cursor.fetchall()
        cursor.execute('SELECT channel_id, title FROM channels')
        channels = cursor.fetchall()
        cursor.execute('SELECT message_id, file_name FROM attachments')
        attachments = cursor.fetchall()
        conn.close()

        self.message_index = {msg_id: content for msg_id, content in messages}
        self.user_index = {user_id: username for user_id, username in users}
        self.channel_index = {chan_id: title for chan_id, title in channels}
        self.attachment_index = {msg_id: file_name for msg_id, file_name in attachments}

    def search(self, query):
        """
        Perform a search on indexed data for the query.
        Returns a dictionary of matches across all entities.
        """
        results = defaultdict(list)

        for msg_id, content in self.message_index.items():
            if re.search(r'\b' + re.escape(query) + r'\b', content, re.IGNORECASE):
                results['messages'].append((msg_id, content))

        for user_id, username in self.user_index.items():
            if re.search(r'\b' + re.escape(query) + r'\b', username, re.IGNORECASE):
                results['users'].append((user_id, username))

        for chan_id, title in self.channel_index.items():
            if re.search(r'\b' + re.escape(query) + r'\b', title, re.IGNORECASE):
                results['channels'].append((chan_id, title))

        for msg_id, file_name in self.attachment_index.items():
            if re.search(r'\b' + re.escape(query) + r'\b', file_name, re.IGNORECASE):
                results['attachments'].append((msg_id, file_name))

        print("Search Results for:", query)
        for entity, matches in results.items():
            print(f"{entity.capitalize()} Matches:")
            for match in matches:
                print(match)

        return results
