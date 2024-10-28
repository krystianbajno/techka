from techka.telegram.telegram_client import TelegramClientManager
from techka.telegram.telegram_database import DatabaseManager
from techka.auth.auth_service import AuthService
import sqlite3
import os
import re
from collections import defaultdict, Counter
from datetime import datetime
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch, PeerChannel, MessageMediaDocument
from telethon.tl.functions.messages import GetHistoryRequest

class TelegramService:
    def __init__(self, auth_service, identity_name):
        self.auth_service = auth_service
        self.identity_name = identity_name

        # Initialize Telegram Client and Database Manager
        self.client_manager = TelegramClientManager(auth_service, identity_name)
        self.client = self.client_manager.get_client()
        self.db_manager = DatabaseManager()

    ### COLLECTION PHASE ###

    def collect_channels(self):
        """ Collect all channels from the logged-in account and save them in the database """
        if not self.client.is_user_authorized():
            self.client_manager._initialize_client()

        conn = sqlite3.connect(self.db_manager.db_name)
        cursor = conn.cursor()

        dialogs = self.client.get_dialogs()
        for dialog in dialogs:
            if dialog.is_channel:
                channel = dialog.entity
                cursor.execute('''
                    INSERT OR IGNORE INTO channels (channel_id, title, username, date_created)
                    VALUES (?, ?, ?, ?)
                ''', (channel.id, channel.title, channel.username, channel.date))
        conn.commit()
        conn.close()

    def collect_users_in_channel(self, channel_name):
        """ Collect all users in a specific channel and save them in the database """
        if not self.client.is_user_authorized():
            self.client_manager._initialize_client()

        channel = self.client.get_entity(channel_name)
        all_participants = []
        offset = 0
        limit = 100

        while True:
            participants = self.client(GetParticipantsRequest(
                channel,
                ChannelParticipantsSearch(''),
                offset=offset,
                limit=limit,
                hash=0
            ))
            if not participants.users:
                break

            all_participants.extend(participants.users)
            offset += len(participants.users)

        for user in all_participants:
            profile = {
                'user_id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'bio': ''  # Use GetFullUser if you need a detailed profile
            }
            self.db_manager.save_user_profile(profile, channel.id)

    def collect_messages_from_channel(self, channel_name):
        """ Collect all messages from a specific channel and save them in the database """
        if not self.client.is_user_authorized():
            self.client_manager._initialize_client()

        channel = self.client.get_entity(channel_name)

        conn = sqlite3.connect(self.db_manager.db_name)
        cursor = conn.cursor()

        offset_id = 0
        limit = 100

        while True:
            history = self.client(GetHistoryRequest(
                peer=PeerChannel(channel.id),
                limit=limit,
                offset_id=offset_id,
                max_id=0,
                min_id=0,
                add_offset=0,
                hash=0
            ))

            if not history.messages:
                break

            for message in history.messages:
                user_id = message.from_id.user_id if message.from_id else None
                cursor.execute('''
                    INSERT OR IGNORE INTO messages (message_id, channel_id, user_id, date, content)
                    VALUES (?, ?, ?, ?, ?)
                ''', (message.id, channel.id, user_id, message.date.strftime("%Y-%m-%d %H:%M:%S"), message.message))
                
                # Collect attachments if they exist
                if message.media and isinstance(message.media, MessageMediaDocument):
                    self.collect_attachment(message)

            offset_id = history.messages[-1].id
            conn.commit()
        conn.close()

    def collect_attachment(self, message):
        """ Collect any attachments from a message """
        if not os.path.exists('attachments'):
            os.makedirs('attachments')

        file_path = self.client.download_media(message, file='attachments/')
        if file_path:
            file_name = os.path.basename(file_path)
            file_type = os.path.splitext(file_name)[1].replace('.', '')
            
            # Save attachment in the database
            conn = sqlite3.connect(self.db_manager.db_name)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO attachments (message_id, file_name, file_type, file_path)
                VALUES (?, ?, ?, ?)
            ''', (message.id, file_name, file_type, file_path))
            conn.commit()
            conn.close()
            print(f'Downloaded attachment to {file_path}')

    def collect_all_users_from_all_channels(self):
        """ Collect and save all users from all stored channels in the database """
        conn = sqlite3.connect(self.db_manager.db_name)
        cursor = conn.cursor()

        cursor.execute('SELECT channel_id, title FROM channels')
        channels = cursor.fetchall()

        for channel_id, channel_name in channels:
            print(f"Collecting users in channel: {channel_name}")
            self.collect_users_in_channel(channel_name)

        conn.close()

    ### PROCESSING PHASE ###

    def check_and_collect_data(self, table_name, collect_method, *args):
        """ Check if the database table has data; if not, trigger data collection """
        conn = sqlite3.connect(self.db_manager.db_name)
        cursor = conn.cursor()
        cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
        count = cursor.fetchone()[0]
        conn.close()

        if count == 0:
            print(f'No data found in {table_name}. Collecting data...')
            collect_method(*args)

    def process_user_interactions(self, channel_name):
        """ Process user interactions for posts in a specific channel """
        self.check_and_collect_data('channels', self.collect_channels)
        self.check_and_collect_data('messages', self.collect_messages_from_channel, channel_name)
        
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
        """ Analyze messages in a channel for specific keywords """
        self.check_and_collect_data('channels', self.collect_channels)
        self.check_and_collect_data('messages', self.collect_messages_from_channel, channel_name)
        
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

    def extract_data_for_analysis(self):
        """ Extract messages and attachments for external analysis """
        conn = sqlite3.connect(self.db_manager.db_name)
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM messages')
        messages = cursor.fetchall()

        cursor.execute('SELECT * FROM attachments')
        attachments = cursor.fetchall()

        conn.close()
        return {'messages': messages, 'attachments': attachments}
    

def get_first_telegram_identity(auth_service):
    """ Helper function to get the first Telegram identity from the AuthService """
    identities = auth_service.get_all_identities_for_service('Telegram')
    if identities:
        return identities[0]
    else:
        print("No Telegram identities found in AuthService.")
        exit(1)
