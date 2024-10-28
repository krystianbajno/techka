from techka.telegram.telegram_service import TelegramService

class TelegramHandler:
    def __init__(self, auth_service):
        self.telegram_service = TelegramService(auth_service)

    def init_commands(self, subparsers):
        telegram_parser = subparsers.add_parser("telegram", help="Telegram related commands")
        telegram_subparsers = telegram_parser.add_subparsers(dest="action", required=True)
        
        # Collect Command
        telegram_collect_parser = telegram_subparsers.add_parser("collect", help="Collect data from Telegram")
        telegram_collect_parser.add_argument("--channels", action="store_true", help="Collect all channels")
        telegram_collect_parser.add_argument("--users", action="store_true", help="Collect all users or users from a specific channel if --channel is provided")
        telegram_collect_parser.add_argument("--messages", action="store_true", help="Collect all messages, or messages from a specific channel if --channel is provided")
        telegram_collect_parser.add_argument("--user-messages", type=int, help="Collect all messages from a specific user across channels")
        telegram_collect_parser.add_argument("--channel", type=str, help="Specify the channel for user or message collection")
        telegram_collect_parser.add_argument("--monitor-channel", type=str, help="Real-time monitoring for a specific channel")
        telegram_collect_parser.add_argument("--monitor-all", action="store_true", help="Real-time monitoring for all channels")
        telegram_collect_parser.add_argument("--monitor-user", type=str, help="Real-time monitoring for messages from a specific user")

        # Display Command
        telegram_display_parser = telegram_subparsers.add_parser("display", help="Display collected Telegram data")
        telegram_display_parser.add_argument("--channels", action="store_true", help="Display all collected channels, or channels for a specific user if --user is provided")
        telegram_display_parser.add_argument("--users", action="store_true", help="Display all users or users in a specific channel if --channel is provided")
        telegram_display_parser.add_argument("--messages", action="store_true", help="Display all messages or messages from a specific user or channel if specified")
        telegram_display_parser.add_argument("--user", type=int, help="Limit channels or messages display to a specific user")
        telegram_display_parser.add_argument("--channel", type=str, help="Limit users or messages display to a specific channel")

        # Process Command
        telegram_process_parser = telegram_subparsers.add_parser("process", help="Process collected Telegram data")
        telegram_process_parser.add_argument("--user-interactions", action="store_true", help="Analyze user interactions in a specific channel")
        telegram_process_parser.add_argument("--keywords", nargs="+", help="Analyze messages for specific keywords in a channel")
        telegram_process_parser.add_argument("--channel", type=str, help="Specify the channel for processing")
        telegram_process_parser.add_argument("--social-graph", action="store_true", help="Build and analyze a social network graph")

        # Export Command
        telegram_export_parser = telegram_subparsers.add_parser("export", help="Export Telegram attachments")
        telegram_export_parser.add_argument("--export-dir", type=str, required=True, help="Directory to export attachments to")
        telegram_export_parser.add_argument("--attachment-type", type=str, help="Filter attachments by type (e.g., image, pdf)")
        telegram_export_parser.add_argument("--channel-id", type=int, help="Specify the channel ID for attachment retrieval")
        telegram_export_parser.add_argument("--user-id", type=int, help="Specify the user ID for attachment retrieval")

        # Search Command
        telegram_search_parser = telegram_subparsers.add_parser("search", help="Search through collected Telegram data")
        telegram_search_parser.add_argument("query", type=str, help="Search query for messages, users, channels, or attachments")

    def handle(self, args):
        action_map = {
            "collect": self._collect,
            "process": self._process,
            "display": self._display,
            "export": self._export,
            "search": self._search,
        }
        action = args.action
        if action in action_map:
            action_map[action](args)

    def _collect(self, args):
        if args.channels:
            self.telegram_service.collect_all_channels()
            print("Collected all channels.")

        if args.users:
            if args.channel:
                self.telegram_service.collect_all_participants_in_channel(args.channel)
                print(f"Collected users from channel: {args.channel}")
            else:
                self.telegram_service.collect_all_users()
                print("Collected users across all channels.")

        if args.messages:
            if args.channel:
                self.telegram_service.collect_messages_in_channel(args.channel)
            else:
                self.telegram_service.collect_all_messages()
                print("Collected all messages across channels.")

        if args.user_messages:
            self.telegram_service.collect_messages_from_user(args.user_messages)
            print(f"Collected all messages from user ID: {args.user_messages}")

        if args.monitor_channel:
            self.telegram_service.start_realtime_monitoring_for_channel(args.monitor_channel)
            print(f"Started real-time monitoring for channel: {args.monitor_channel}")

        if args.monitor_all:
            self.telegram_service.start_realtime_monitoring_for_all_channels()
            print("Started real-time monitoring for all channels.")

        if args.monitor_user:
            self.telegram_service.start_realtime_monitoring_for_user(args.monitor_user)
            print(f"Started real-time monitoring for user: {args.monitor_user}")

    def _process(self, args):
        if args.user_interactions:
            if args.channel:
                interactions = self.telegram_service.analyze_user_activity_in_channel(args.channel)
                print(f"User interactions in channel {args.channel}:")
                for interaction in interactions:
                    print(interaction)
            else:
                print("Please provide a channel using --channel.")

        if args.keywords:
            if args.channel:
                keyword_analysis = self.telegram_service.keyword_analysis_in_channel(args.keywords, args.channel)
                print(f"Keywords found in channel {args.channel}: {keyword_analysis}")
            else:
                print("Please provide a channel using --channel.")

        if args.social_graph:
            self.telegram_service.build_social_network_graph()
            print("Social network graph generated and analyzed.")

    def _display(self, args):
        if args.channels:
            if args.user:
                self.telegram_service.display_channels_for_user(args.user)
                print(f"Channels for user ID {args.user}:")
            else:
                self.telegram_service.display_all_channels()
                print("All collected channels:")

        if args.users:
            if args.channel:
                self.telegram_service.display_users_in_channel(args.channel)
            else:
                self.telegram_service.display_all_users()

        if args.messages:
            if args.user and args.channel:
                messages = self.telegram_service.display_messages_from_user_in_channel(args.user, args.channel)
                print(f"Messages from user ID {args.user} in channel {args.channel}.")
            elif args.user:
                messages = self.telegram_service.display_messages_from_user(args.user)
                print(f"All messages from user ID {args.user} across all channels.")
            elif args.channel:
                messages = self.telegram_service.display_messages_in_channel(args.channel)
                print(f"Messages in channel {args.channel}.")
            else:
                messages = self.telegram_service.display_all_messages()
                

    def _export(self, args):
        export_dir = args.export_dir
        attachment_type = args.attachment_type
        channel_id = args.channel_id
        user_id = args.user_id

        self.telegram_service.export_attachments(export_dir, attachment_type=attachment_type, channel_id=channel_id, user_id=user_id)
        print(f"Attachments exported to {export_dir}")

    def _search(self, args):
        search_results = self.telegram_service.search_collected_data(args.query)
        print(f"Search results for '{args.query}':")
        for entity_type, results in search_results.items():
            print(f"{entity_type.capitalize()} Matches:")
            for result in results:
                print(result)
