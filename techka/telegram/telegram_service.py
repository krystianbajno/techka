import os
import sqlite3
import shutil
import networkx as nx
from techka.telegram.telegram_client import TelegramClientManager
from techka.telegram.telegram_database import DatabaseManager
from techka.telegram.data_collection import DataCollector
from techka.telegram.data_display import DataDisplay
from techka.telegram.data_processing import DataProcessor
from techka.telegram.intelligence_analysis import IntelligenceAnalysis
from techka.telegram.search_and_storage import DataIndexer

class TelegramService:
    ATTACHMENTS_DIR = "data/attachments"

    def __init__(self, auth_service):
        self.auth_service = auth_service
        self.client_manager = TelegramClientManager(auth_service)
        self.client = self.client_manager.get_client()
        self.db_manager = DatabaseManager()

        # Initialize modules
        self.data_collector = DataCollector(self.client, self.db_manager)
        self.data_display = DataDisplay(self.db_manager)
        self.data_processor = DataProcessor(self.db_manager)
        self.intelligence_analysis = IntelligenceAnalysis(self.client, self.db_manager)
        self.data_indexer = DataIndexer(self.db_manager)

    ### Collection and Data Retrieval ###

    def collect_all_channels(self):
        """Collect all channels the user has access to."""
        self.data_collector.collect_all_channels()

    def collect_all_participants_in_channel(self, channel_name):
        """Collect all users from a specific channel."""
        self.data_collector.collect_active_users_in_channel(channel_name)

    def collect_messages_in_channel(self, channel_name):
        """Collect all messages from a specific channel."""
        self.data_collector.collect_messages_in_channel(channel_name)

    def collect_messages_from_user(self, user_id):
        """Collect all messages from a specific user across all channels."""
        self.data_collector.collect_messages_from_user(user_id)

    def collect_messages_from_multiple_channels(self, channel_names=None):
        """
        Collect all messages from specified channels. 
        If channel_names is None, collects from all available channels.
        """
        self.data_collector.collect_messages_from_multiple_channels(channel_names)

    def collect_all_users(self):
        """Collect all users across all channels."""
        self.data_collector.collect_all_users()
        print("Collected all users across all channels.")
        
    ### Real-time Monitoring ###
    
    def start_realtime_monitoring_for_user(self, user_name):
        """Start real-time monitoring of messages for user."""
        self.intelligence_analysis.start_realtime_monitoring_for_user(user_name)

    def start_realtime_monitoring_for_channel(self, channel_name):
        """Start real-time monitoring of messages in a specific channel."""
        self.intelligence_analysis.start_realtime_monitoring(channel_name)

    def start_realtime_monitoring_for_all_channels(self):
        """Start real-time monitoring of all available channels."""
        self.intelligence_analysis.start_realtime_monitoring_for_all_channels()

    ### Display Collected Data ###

    def display_all_channels(self):
        """Display all collected channels."""
        return self.data_display.display_channels()

    def display_messages_from_user(self, user_id):
        """Display all messages collected from a specific user."""
        return self.data_display.display_messages_from_user(user_id)

    def display_messages_in_channel(self, channel_name):
        """Display all messages in a specified channel."""
        return self.data_display.display_messages_in_channel(channel_name)

    def display_latest_messages_in_channel(self, channel_name, limit=10):
        """Display the latest messages in a specific channel."""
        return self.data_display.display_latest_messages_in_channel(channel_name, limit)

    ### Data Analysis ###

    def analyze_user_activity_in_channel(self, channel_name):
        """Analyze user activity levels in a specified channel."""
        return self.data_processor.analyze_user_activity(channel_name)

    def keyword_analysis_in_channel(self, keywords, channel_name):
        """Analyze messages in a specific channel for specified keywords."""
        return self.data_processor.keyword_analysis_in_channel(keywords, channel_name)

    ### Intelligence and Surveillance ###

    def build_social_network_graph(self, export_path=None):
        """Build a social network graph for all users and interactions and optionally export it."""
        G = self.intelligence_analysis.build_social_graph()

        if export_path:
            # Save the graph in GraphML format for visualization in tools like Gephi
            nx.write_graphml(G, export_path)
            print(f"Social network graph exported to {export_path}")

        return G

    ### Advanced Search ###

    def search_collected_data(self, query):
        """Search for a keyword across all collected entities (channels, users, messages)."""
        return self.data_indexer.search(query)

    ### Updated Attachment Saving with Directory Structure ###

    def save_attachment(self, message, file_type, user_id, channel_id):
        """Download and save the attachment to a structured directory based on channel and user."""
        file_path = self.client.download_media(message, file=self._get_attachment_path(channel_id, user_id, file_type))
        if file_path:
            file_name = os.path.basename(file_path)

            # Store file path in the database
            conn = sqlite3.connect(self.db_manager.db_name)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO attachments (message_id, file_name, file_type, file_path)
                VALUES (?, ?, ?, ?)
            ''', (message.id, file_name, file_type, file_path))
            conn.commit()
            conn.close()
            print(f"Saved {file_type} to {file_path}")

    def _get_attachment_path(self, channel_id, user_id, file_type):
        """Create and return the directory path for storing attachments based on channel, user, and type."""
        channel_dir = os.path.join(self.ATTACHMENTS_DIR, f"channel_{channel_id}")
        user_dir = os.path.join(channel_dir, f"user_{user_id}")
        type_dir = os.path.join(user_dir, file_type + "s")

        os.makedirs(type_dir, exist_ok=True)  # Ensure the directories exist
        return type_dir

    ### Attachment Retrieval and Display Methods ###

    def get_all_attachments(self):
        """Retrieve all attachment paths."""
        conn = sqlite3.connect(self.db_manager.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT file_path, file_name, file_type FROM attachments")
        attachments = cursor.fetchall()
        conn.close()
        return attachments

    def get_attachments_by_type(self, attachment_type):
        """Retrieve attachment paths of a specific type."""
        conn = sqlite3.connect(self.db_manager.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT file_path, file_name, file_type FROM attachments WHERE file_type = ?", (attachment_type,))
        attachments = cursor.fetchall()
        conn.close()
        return attachments

    def get_attachments_by_channel(self, channel_id):
        """Retrieve all attachments from a specific channel."""
        conn = sqlite3.connect(self.db_manager.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT attachments.file_path, attachments.file_name, attachments.file_type
            FROM attachments
            JOIN messages ON attachments.message_id = messages.message_id
            WHERE messages.channel_id = ?
        ''', (channel_id,))
        attachments = cursor.fetchall()
        conn.close()
        return attachments

    def get_attachments_by_user(self, user_id):
        """Retrieve all attachments sent by a specific user across all channels."""
        conn = sqlite3.connect(self.db_manager.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT attachments.file_path, attachments.file_name, attachments.file_type
            FROM attachments
            JOIN messages ON attachments.message_id = messages.message_id
            WHERE messages.user_id = ?
        ''', (user_id,))
        attachments = cursor.fetchall()
        conn.close()
        return attachments

    def get_attachments_by_type_and_channel(self, attachment_type, channel_id):
        """Retrieve all attachments of a specific type from a specific channel."""
        conn = sqlite3.connect(self.db_manager.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT attachments.file_path, attachments.file_name, attachments.file_type
            FROM attachments
            JOIN messages ON attachments.message_id = messages.message_id
            WHERE attachments.file_type = ? AND messages.channel_id = ?
        ''', (attachment_type, channel_id))
        attachments = cursor.fetchall()
        conn.close()
        return attachments

    def get_attachments_by_type_and_user(self, attachment_type, user_id):
        """Retrieve all attachments of a specific type sent by a specific user."""
        conn = sqlite3.connect(self.db_manager.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT attachments.file_path, attachments.file_name, attachments.file_type
            FROM attachments
            JOIN messages ON attachments.message_id = messages.message_id
            WHERE attachments.file_type = ? AND messages.user_id = ?
        ''', (attachment_type, user_id))
        attachments = cursor.fetchall()
        conn.close()
        return attachments

    def export_attachments(self, export_dir, attachment_type=None, channel_id=None, user_id=None):
        """
        Export attachments based on type, channel, user, or a combination of these filters to a specified directory.
        
        Parameters:
            export_dir (str): The path to the export directory.
            attachment_type (str): The type of attachments to export (e.g., "image").
            channel_id (int): The ID of the channel from which to export attachments.
            user_id (int): The ID of the user whose attachments should be exported.
        """
        # Fetch attachments based on filters
        if attachment_type and channel_id:
            attachments = self.get_attachments_by_type_and_channel(attachment_type, channel_id)
        elif attachment_type and user_id:
            attachments = self.get_attachments_by_type_and_user(attachment_type, user_id)
        elif attachment_type:
            attachments = self.get_attachments_by_type(attachment_type)
        elif channel_id:
            attachments = self.get_attachments_by_channel(channel_id)
        elif user_id:
            attachments = self.get_attachments_by_user(user_id)
        else:
            attachments = self.get_all_attachments()

        if not attachments:
            print("No attachments found for the specified criteria.")
            return

        os.makedirs(export_dir, exist_ok=True)

        for file_path, file_name, file_type in attachments:
            sub_dir = export_dir
            if channel_id:
                sub_dir = os.path.join(sub_dir, f"channel_{channel_id}")
            if user_id:
                sub_dir = os.path.join(sub_dir, f"user_{user_id}")
            if attachment_type:
                sub_dir = os.path.join(sub_dir, f"{attachment_type}s")

            os.makedirs(sub_dir, exist_ok=True)

            dest_path = os.path.join(sub_dir, file_name)
            shutil.copy2(file_path, dest_path)
            print(f"Exported {file_name} to {dest_path}")

        print(f"Export completed. Files saved to {export_dir}.")


    def export_all_users(self, export_path):
        """Export all users across all channels to a specified file."""
        users = self.display_all_users()
        
        os.makedirs(os.path.dirname(export_path), exist_ok=True)
        with open(export_path, 'w') as file:
            file.write("User ID, Username, First Name, Last Name\n")
            for user_id, username, first_name, last_name in users:
                file.write(f"{user_id}, {username}, {first_name}, {last_name}\n")
        print(f"Exported all users to {export_path}.")
        
    def display_all_users(self):
        """Display all users across all channels."""
        return self.data_display.display_all_users()
    
    def display_all_messages(self):
        return self.data_display.display_all_messages()
    
    def display_messages_from_user_in_channel(self, user_id, channel_name):
        """Display all messages from a specific user in a specific channel."""
        return self.data_display.display_messages_from_user_in_channel(user_id, channel_name)
    
    
    def display_channels_for_user(self, user_id):
        """Retrieve and display all channels that a specific user has participated in."""
        return self.data_display.display_channels_for_user(user_id)
    
    
    def display_users_in_channel(self, channel_name):
        """Display users in a specific channel."""
        users = self.data_display.display_users_in_channel(channel_name)
        for user_id, username, first_name, last_name in users:
            print(f"User ID: {user_id}, Username: {username}, First Name: {first_name}, Last Name: {last_name}")
        return users