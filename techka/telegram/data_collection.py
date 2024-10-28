import sqlite3
from telethon import TelegramClient
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch, PeerChannel, MessageMediaDocument
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.errors.rpcerrorlist import ChannelPrivateError, ChatAdminRequiredError, RPCError
from telethon.tl.types import Channel, Chat

class DataCollector:
    def __init__(self, client, db_manager):
        self.client: TelegramClient = client
        self.db_manager = db_manager

    ### Channel Collection ###

    def collect_all_channels(self):
        """Collect all channels accessible to the account."""
        dialogs = self.client.get_dialogs()
        for dialog in dialogs:
            if dialog.is_channel:
                self._save_channel(dialog.entity)
                
    def collect_all_users(self):
        """Collect all users across all channels and save them in the database."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        # Fetch all channels from the database
        cursor.execute("SELECT channel_id, title FROM channels")
        channels = cursor.fetchall()

        for channel_id, channel_name in channels:
            print(f"Collecting users in channel: {channel_name}")
            self.collect_users_in_channel(channel_name)

        conn.close()
        
    def collect_active_users_in_channel(self, entity_name_or_id):
        """Collect active users by retrieving messages from the specified entity."""
        try:
            # Get the entity (could be channel, group, or chat)
            entity = self.client.get_entity(entity_name_or_id)
            active_users = set()  # Store unique user IDs to avoid duplicates

            # Iterate over messages to collect active users
            for message in self.client.iter_messages(entity):
                if message.sender_id:  # Ensure there is a sender
                    active_users.add(message.sender_id)
                    
                    # Save user information in the database
                    user_data = {
                        'user_id': message.sender_id,
                        'username': message.from_id.user_id if message.from_id else None,
                        'first_name': message.sender.first_name if message.sender else None,
                        'last_name': message.sender.last_name if message.sender else None,
                    }
                    self.db_manager.save_user(user_data, entity.id)
                    print(f"Collected active user: {user_data}")

            print(f"Collected {len(active_users)} unique active users from '{entity_name_or_id}'.")

        except RPCError as e:
            print(f"Failed to retrieve messages from '{entity_name_or_id}': {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def collect_users_in_channel(self, channel_name):
        """Collect all participants in the specified channel or group."""
        try:
            # Resolve the entity for the given channel name
            entity = self.client.get_entity(channel_name)
            
            # Ensure the entity is a Channel or Chat type
            if not isinstance(entity, (Channel, Chat)):
                print(f"The provided entity '{channel_name}' is not a valid channel or group.")
                return

            all_participants = []
            offset = 0
            limit = 100  # Telegram API limit

            # Loop through participants with pagination
            while True:
                participants = self.client(GetParticipantsRequest(
                    entity,
                    ChannelParticipantsSearch(''),
                    offset=offset,
                    limit=limit,
                    hash=0
                ))

                if not participants.users:
                    break  # Exit loop if no more users

                all_participants.extend(participants.users)
                offset += len(participants.users)

                # Save each user in the database
                for participant in participants.users:
                    user_data = {
                        'user_id': participant.id,
                        'username': participant.username,
                        'first_name': participant.first_name,
                        'last_name': participant.last_name,
                    }
                    self.db_manager.save_user(user_data, entity.id)

                print(f"Processed {len(participants.users)} users in the current batch for {channel_name}.")

            print(f"Collected all users in '{channel_name}'. Total users: {len(all_participants)}")

        except ChannelPrivateError:
            print(f"Cannot access the channel '{channel_name}' because it is private.")
        except ChatAdminRequiredError:
            print(f"Cannot access participants in '{channel_name}' - Admin privileges required.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def _save_channel(self, channel):
        """Helper method to save a channel to the database."""
        conn = sqlite3.connect(self.db_manager.db_name)
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM channels WHERE channel_id = ?', (channel.id,))
        if cursor.fetchone() is None:
            cursor.execute('''
                INSERT INTO channels (channel_id, title, username, date_created)
                VALUES (?, ?, ?, ?)
            ''', (channel.id, channel.title, channel.username, channel.date))
            print(f"Collected and saved channel: {channel.title}")
        conn.commit()
        conn.close()

    ### Message Collection ###

    def collect_messages_in_channel(self, channel_name):
        """Collect all messages from a specific channel."""
        channel = self.client.get_entity(channel_name)
        offset_id, limit = 0, 100

        while True:
            history = self.client(GetHistoryRequest(
                peer=PeerChannel(channel.id), limit=limit, offset_id=offset_id,
                max_id=0, min_id=0, add_offset=0, hash=0))

            if not history.messages:
                break

            for message in history.messages:
                self._save_message(message, channel.id)
                if message.media and isinstance(message.media, MessageMediaDocument):
                    self._save_attachment(message)

            offset_id = history.messages[-1].id

    def collect_messages_from_user(self, user_id):
        """Collect all messages across channels sent by a specific user."""
        conn = sqlite3.connect(self.db_manager.db_name)
        cursor = conn.cursor()
        cursor.execute('SELECT channel_id FROM channels')
        channels = cursor.fetchall()
        
        for (channel_id,) in channels:
            self._collect_messages_from_user_in_channel(user_id, channel_id)

    def _collect_messages_from_user_in_channel(self, user_id, channel_id):
        """Helper method to collect messages from a specific user within a specific channel."""
        channel = PeerChannel(channel_id)
        offset_id, limit = 0, 100

        while True:
            history = self.client(GetHistoryRequest(
                peer=channel, limit=limit, offset_id=offset_id,
                max_id=0, min_id=0, add_offset=0, hash=0))
            
            if not history.messages:
                break

            for message in history.messages:
                if message.from_id.user_id == user_id:
                    self._save_message(message, channel_id)
                    if message.media and isinstance(message.media, MessageMediaDocument):
                        self._save_attachment(message)

            offset_id = history.messages[-1].id

    def collect_messages_from_multiple_channels(self, channel_names=None):
        """
        Collect messages from specified channels, or all channels if none are specified.
        """
        conn = sqlite3.connect(self.db_manager.db_name)
        cursor = conn.cursor()

        if channel_names:
            cursor.execute('SELECT channel_id FROM channels WHERE title IN (?)', (channel_names,))
        else:
            cursor.execute('SELECT channel_id FROM channels')
        
        channels = cursor.fetchall()
        for (channel_id,) in channels:
            self.collect_messages_in_channel(channel_id)

    def _save_message(self, message, channel_id):
        """Helper method to save a message to the database."""
        conn = sqlite3.connect(self.db_manager.db_name)
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM messages WHERE message_id = ?', (message.id,))
        if cursor.fetchone() is None:
            cursor.execute('''
                INSERT INTO messages (message_id, channel_id, user_id, date, content)
                VALUES (?, ?, ?, ?, ?)
            ''', (message.id, channel_id, message.from_id.user_id, message.date.strftime("%Y-%m-%d %H:%M:%S"), message.message))
            print(f"Collected message ID: {message.id}")
        conn.commit()
        conn.close()

    ### Attachment Collection ###

    def _save_attachment(self, message):
        """Helper method to save attachments from a message to the database."""
        file_path = self.client.download_media(message, file='attachments/')
        if file_path:
            conn = sqlite3.connect(self.db_manager.db_name)
            cursor = conn.cursor()
            file_name = os.path.basename(file_path)
            file_type = os.path.splitext(file_name)[1].replace('.', '')
            cursor.execute('''
                INSERT INTO attachments (message_id, file_name, file_type, file_path)
                VALUES (?, ?, ?, ?)
            ''', (message.id, file_name, file_type, file_path))
            conn.commit()
            conn.close()
            print(f'Downloaded and saved attachment to {file_path}')
