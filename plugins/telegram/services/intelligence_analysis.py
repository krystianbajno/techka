from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import PeerChannel
import sqlite3
import networkx as nx
import threading
import re
import time
from telethon import events

class IntelligenceAnalysis:
    def __init__(self, client, db_manager):
        self.client = client
        self.db_manager = db_manager

    ### Real-Time Monitoring ###

    def start_realtime_monitoring(self, channel_name):
        """Monitor a specific channel in real-time and log all new messages."""
        channel = self.client.get_entity(channel_name)
        print(f"Starting real-time monitoring for channel: {channel.title}")
        
        def monitor():
            while True:
                history = self.client(GetHistoryRequest(
                    peer=PeerChannel(channel.id),
                    limit=1,
                    offset_date=None,
                    add_offset=0,
                    max_id=0,
                    min_id=0,
                    hash=0
                ))
                
                if history.messages:
                    message = history.messages[0]
                    self._log_message(message, channel.id)
                    print(f"Real-time message in {channel.title}: {message.message}")

                time.sleep(2)  # Polling interval

        threading.Thread(target=monitor, daemon=True).start()

    def start_realtime_monitoring_for_all_channels(self):
        """Monitor all channels in real-time."""
        conn = sqlite3.connect(self.db_manager.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT title FROM channels")
        channels = cursor.fetchall()
        conn.close()

        for (channel_name,) in channels:
            self.start_realtime_monitoring(channel_name)
            
    def start_realtime_monitoring_for_user(self, user_name):
        """
        Start real-time monitoring of messages for a specific user by username.
        
        Parameters:
            user_name (str): The username of the user to monitor.
        """
        user = self.client.get_entity(user_name)
        
        print(f"Starting real-time monitoring for user: {user_name}")

        @self.client.on(events.NewMessage(from_user=user))
        async def handler(event):
            message_data = {
                'message_id': event.message.id,
                'user_id': user.id,
                'channel_id': event.chat_id if event.is_channel else None,
                'date': event.message.date.strftime("%Y-%m-%d %H:%M:%S"),
                'content': event.message.message
            }

            self.db_manager.save_message(message_data)
            print(f"New message from {user_name}: {event.message.message}")

        self.client.run_until_disconnected()

    def _log_message(self, message, channel_id):
        """Helper method to log a new message to the database."""
        conn = sqlite3.connect(self.db_manager.db_name)
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM messages WHERE message_id = ?', (message.id,))
        if cursor.fetchone() is None:
            cursor.execute('''
                INSERT INTO messages (message_id, channel_id, user_id, date, content)
                VALUES (?, ?, ?, ?, ?)
            ''', (message.id, channel_id, message.from_id.user_id, message.date.strftime("%Y-%m-%d %H:%M:%S"), message.message))
            conn.commit()
        conn.close()

    ### Social Network Analysis ###

    def build_social_graph(self):
        """Build and analyze a social graph based on user interactions across messages."""
        G = nx.DiGraph()  # Directed graph for social interactions
        conn = sqlite3.connect(self.db_manager.db_name)
        cursor = conn.cursor()

        # Fetch all messages with users
        cursor.execute('''
            SELECT user_id, channel_id FROM messages
        ''')
        interactions = cursor.fetchall()
        conn.close()

        for user_id, channel_id in interactions:
            G.add_node(user_id)
            G.add_edge(user_id, channel_id)

        print("Social Network Analysis:")
        print("Number of Nodes (Users/Channels):", G.number_of_nodes())
        print("Number of Edges (Interactions):", G.number_of_edges())

        # Identify key influencers using centrality
        centrality = nx.degree_centrality(G)
        top_influencers = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:10]
        print("Top 10 Influencers (User IDs):")
        for influencer, score in top_influencers:
            print(f"User ID: {influencer}, Influence Score: {score}")

    ### Keyword Monitoring ###

    def realtime_keyword_monitoring(self, keywords):
        """Monitor all messages for specified keywords in real-time."""
        conn = sqlite3.connect(self.db_manager.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT title FROM channels")
        channels = cursor.fetchall()
        conn.close()

        def monitor_channel_keywords(channel_name):
            channel = self.client.get_entity(channel_name)
            print(f"Keyword monitoring started for channel: {channel.title}")

            def monitor():
                while True:
                    history = self.client(GetHistoryRequest(
                        peer=PeerChannel(channel.id),
                        limit=1,
                        offset_date=None,
                        add_offset=0,
                        max_id=0,
                        min_id=0,
                        hash=0
                    ))

                    if history.messages:
                        message = history.messages[0]
                        for keyword in keywords:
                            if re.search(r'\b' + re.escape(keyword) + r'\b', message.message, re.IGNORECASE):
                                print(f"Keyword '{keyword}' found in {channel.title}: {message.message}")
                                self._log_message(message, channel.id)

                    time.sleep(2)  # Polling interval

            threading.Thread(target=monitor, daemon=True).start()

        for (channel_name,) in channels:
            monitor_channel_keywords(channel_name)
