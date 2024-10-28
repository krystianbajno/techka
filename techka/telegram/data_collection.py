from io import BytesIO
import os
import sqlite3
import time
from telethon import TelegramClient
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch, PeerChannel, MessageMediaPhoto, MessageMediaDocument, PeerUser, MessageMediaPoll, MessageMediaWebPage
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.errors.rpcerrorlist import ChannelPrivateError, ChatAdminRequiredError, RPCError, MessageNotModifiedError
from telethon.tl.types import Channel, Chat
from techka.telegram.telegram_database import DatabaseManager
from telethon.tl.types import (
    MessageMediaDocument, MessageMediaPhoto, Document, Photo, 
    DocumentAttributeFilename, PeerUser
)
from tqdm import tqdm  # Use tqdm for a clean progress bar

class DataCollector:
    def __init__(self, client, db_manager):
        self.client: TelegramClient = client
        self.db_manager: DatabaseManager = db_manager

    ### Channel Collection ###
    def collect_all_channels(self):
        """Collect all accessible channels, groups, and supergroups and save them with member counts."""
        dialogs = self.client.get_dialogs()
        for dialog in dialogs:
            if isinstance(dialog.entity, (Channel, Chat)):
                entity = dialog.entity
                channel_type = self._determine_channel_type(entity)

                member_count = getattr(entity, 'participant_count', 0)
                date_created = entity.date.strftime("%Y-%m-%d %H:%M:%S") if entity.date else None

                self.db_manager.save_channel_info(
                    channel_id=entity.id,
                    title=entity.title,
                    username=getattr(entity, 'username', None),
                    channel_type=channel_type,
                    member_count=member_count,
                    date_created=date_created
                )
                print(f"Collected: {entity.id}, {entity.title}, {channel_type}, Members/Subscribers: {member_count}")

    def _determine_channel_type(self, entity):
        """Determine the type of a channel entity: channel, group, or supergroup."""
        if hasattr(entity, 'broadcast') and entity.broadcast:
            return "channel"  # Regular broadcast channel
        elif hasattr(entity, 'megagroup') and entity.megagroup:
            return "supergroup"  # Large discussion group
        else:
            return "group"  # Regular group
        
    def _get_member_count(self, entity):
        """Get the member count for the channel, group, or supergroup."""
        try:
            participants = self.client.get_participants(entity)
            return participants.total  # Member count
        except Exception as e:
            print(f"Error retrieving member count for {entity.title}: {e}")
            return 0  # Default if count retrieval fails

    def collect_all_users(self):
        """Collect all users across all channels and save them in the database."""
        conn = sqlite3.connect(self.db_manager.db_name)
        cursor = conn.cursor()

        cursor.execute("SELECT channel_id, title FROM channels")
        channels = cursor.fetchall()

        for channel_id, channel_name in channels:
            print(f"Collecting users in channel: {channel_name}")
            self.collect_active_users_in_channel(channel_name)

        conn.close()
        
    def collect_active_users_in_channel(self, entity_name_or_id):
        """Collect active users by retrieving messages from the specified entity."""
        try:
            entity = self.client.get_entity(entity_name_or_id)
            active_users = set()

            for message in self.client.iter_messages(entity):
                # Check if sender is a user and extract user_id safely
                if isinstance(message.from_id, PeerUser):
                    user_id = message.from_id.user_id
                    active_users.add(user_id)

                    user_data = {
                        'user_id': user_id,
                        'username': getattr(message.sender, 'username', None),
                        'first_name': getattr(message.sender, 'first_name', None),
                        'last_name': getattr(message.sender, 'last_name', None),
                    }
                    self.db_manager.save_user(user_data, entity.id)
                    print(f"Collected active user: {user_data}")

            print(f"Collected {len(active_users)} unique active users from '{entity_name_or_id}'.")

        except RPCError as e:
            print(f"Failed to retrieve messages from '{entity_name_or_id}': {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            
    def collect_users_in_channel(self, channel_name):
        try:
            entity = self.client.get_entity(channel_name)
            
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

    def collect_messages_in_channel(self, channel_identifier):
        """Collect all messages from a specific channel or group, using either name or ID."""
        # Determine if the identifier is an ID or a name
        channel_identifier = int(channel_identifier)
        entity = PeerChannel(channel_identifier)
        channel_id = channel_identifier  # Directly use the identifier as channel_id


        offset_id, limit = 0, 100

        while True:
            try:
                history = self.client(GetHistoryRequest(
                    peer=entity,
                    limit=limit,
                    offset_id=offset_id,
                    offset_date=None,
                    max_id=0,
                    min_id=0,
                    add_offset=0,
                    hash=0
                ))

                if not history.messages:
                    break

                for message in history.messages:
                    self._save_message(message, channel_id)
                    if message.media and isinstance(message.media, MessageMediaDocument):
                        self._save_attachment(message)

                offset_id = history.messages[-1].id

            except Exception as e:
                print(f"Failed to retrieve messages: {e}")
                break

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
        conn = sqlite3.connect(self.db_manager.db_name)
        cursor = conn.cursor()

        if channel_names:
            cursor.execute('SELECT channel_id FROM channels WHERE title IN (?) or channel_id in (?)', (channel_names,channel_names,))
        else:
            cursor.execute('SELECT channel_id FROM channels')
        
        channels = cursor.fetchall()
        for (channel_id,) in channels:
            self.collect_messages_in_channel(channel_id)

    def _save_message(self, message, channel_id):
        """Save a message to the database, including its date and handling cases where user_id is missing."""
        conn = sqlite3.connect(self.db_manager.db_name)
        cursor = conn.cursor()

        user_id = message.from_id.user_id if isinstance(message.from_id, PeerUser) else None
        message_date = message.date.strftime("%Y-%m-%d %H:%M:%S") if message.date else None

        cursor.execute('SELECT 1 FROM messages WHERE message_id = ?', (message.id,))
        if cursor.fetchone() is None:
            cursor.execute('''
                INSERT INTO messages (message_id, channel_id, user_id, date, content)
                VALUES (?, ?, ?, ?, ?)
            ''', (message.id, channel_id, user_id, message_date, message.message))
            print(f"Collected message ID: {message.id}, Date: {message_date}")

        conn.commit()
        conn.close()

    def _save_attachment(self, message, retries=3):
        """Save attachment, checking for duplicates with (message_id, file_name) as the unique key."""
        conn = sqlite3.connect(self.db_manager.db_name)
        cursor = conn.cursor()

        document = message.media.document if isinstance(message.media, MessageMediaDocument) else None
        if not document:
            print(f"No document found in message ID {message.id}")
            return

        # Extract file name and define the file path
        file_name = self._get_file_name(document)
        file_path = os.path.join('attachments/', file_name)

        # Check if the attachment already exists
        cursor.execute('SELECT 1 FROM attachments WHERE message_id = ? AND file_name = ?', (message.id, file_name))
        if cursor.fetchone():
            print(f"Skipping duplicate attachment for message ID {message.id} with file name {file_name}")
            conn.close()
            return  # Skip the download if it exists

        print(f"Starting download for message ID {message.id} with file name {file_name}")
        attempt = 0

        while attempt < retries:
            try:
                with open(file_path, 'wb') as file:
                    buffer = BytesIO()
                    self.client.download_media(document, file=buffer)
                    buffer.seek(0)  # Reset buffer position for reading
                    file.write(buffer.read())

                # Extract metadata and save details to the database
                mime_type = document.mime_type or "application/octet-stream"
                file_size = document.size
                cursor.execute('''
                    INSERT INTO attachments (message_id, file_name, file_type, file_path, mime_type, size)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (message.id, file_name, mime_type.split('/')[-1], file_path, mime_type, file_size))
                print(f"Successfully downloaded and saved {mime_type} for message ID {message.id} at {file_path}")

                conn.commit()
                break  # Exit retry loop on successful download

            except TimeoutError:
                attempt += 1
                wait_time = 2 ** attempt
                print(f"TimeoutError, retry {attempt}/{retries}. Waiting {wait_time} seconds.")
                time.sleep(wait_time)
            except Exception as e:
                print(f"Unexpected error during download for message ID {message.id}: {e}")
                break
            
        conn.close()

    def _get_file_name(self, document):
        """Extract or create a file name for the document."""
        for attr in document.attributes:
            if isinstance(attr, DocumentAttributeFilename):
                return attr.file_name
        return f"{document.id}.dat"  # Default to document ID if no file name