import argparse
import os
from techka.website.collect import collect
from techka.website.processing import clean_data, get_emails, get_subdomains
from techka.auth.auth_service import AuthService
from techka.telegram.telegram_service import TelegramService, get_first_telegram_identity

DATA_DIR = "data/output"

class CliHandler:
    def __init__(self):
        self.auth_service = AuthService()
        self.parser = argparse.ArgumentParser(description="SOCMINT C4ISR - surveillance and reconnaissance.")
        self.subparsers = self.parser.add_subparsers(dest="command", required=True)

        self._init_website_commands()
        self._init_file_commands()
        self._init_telegram_commands()

        self.command_map = {
            "website": self._handle_website_command,
            "file": self._handle_file_command,
            "telegram": self._handle_telegram_command,
        }

    def _init_website_commands(self):
        """ Initialize website-related commands """
        website_parser = self.subparsers.add_parser("website", help="Website related commands")
        website_subparsers = website_parser.add_subparsers(dest="action", required=True)

        collect_parser = website_subparsers.add_parser("collect", help="Collect data from a website")
        collect_parser.add_argument("url", type=str, help="The target URL")
        collect_parser.add_argument("--auth-header", type=str, help="Authentication header in the format 'Key=Value'", required=False)
        collect_parser.add_argument("--target-only", action="store_true", help="Target only, no subdomains", required=False)

        website_subparsers.add_parser("clean", help="Remove all scraped data")

        process_parser = website_subparsers.add_parser("process", help="Process collected data")
        process_parser.add_argument("--subdomains", action="store_true", help="Extract subdomains")
        process_parser.add_argument("--emails", action="store_true", help="Extract emails from the collected data (includes PDFs)")
        process_parser.add_argument("--pdfs", action="store_true", help="Extract and print text from PDFs and documents")
        process_parser.add_argument("--keywords", nargs="+", help="List of keywords to search for (includes PDFs)")

    def _init_file_commands(self):
        """ Initialize file-related commands """
        file_parser = self.subparsers.add_parser("file", help="File related commands")
        file_subparsers = file_parser.add_subparsers(dest="action", required=True)

        file_process_parser = file_subparsers.add_parser("process", help="Process a file")
        file_process_parser.add_argument("filepath", type=str, help="Path to the file to process")
        file_process_parser.add_argument("--emails", action="store_true", help="Extract emails from the file (includes PDFs)")
        file_process_parser.add_argument("--pdfs", action="store_true", help="Extract and print text from PDFs and documents")
        file_process_parser.add_argument("--keywords", nargs="+", help="List of keywords to search for (includes PDFs)")

    def _init_telegram_commands(self):
        """ Initialize Telegram-related commands """
        telegram_parser = self.subparsers.add_parser("telegram", help="Telegram related commands")
        telegram_subparsers = telegram_parser.add_subparsers(dest="action", required=True)

        telegram_collect_parser = telegram_subparsers.add_parser("collect", help="Collect data from Telegram")
        telegram_collect_parser.add_argument("--channels", action="store_true", help="Collect all channels")
        telegram_collect_parser.add_argument("--users", action="store_true", help="Collect all users from a specific channel")
        telegram_collect_parser.add_argument("--messages", action="store_true", help="Collect all messages from a specific channel")
        telegram_collect_parser.add_argument("--channel", type=str, help="Specify the channel for user or message collection")

        telegram_process_parser = telegram_subparsers.add_parser("process", help="Process collected Telegram data")
        telegram_process_parser.add_argument("--user-interactions", action="store_true", help="Analyze user interactions in a specific channel")
        telegram_process_parser.add_argument("--keywords", nargs="+", help="Analyze messages for specific keywords in a channel")
        telegram_process_parser.add_argument("--channel", type=str, help="Specify the channel for processing")

    def execute(self, args=None):
        parsed_args = self.parser.parse_args(args)
        command = parsed_args.command

        if command in self.command_map:
            self.command_map[command](parsed_args)
        else:
            print(f"Unknown command: {command}")

    def _handle_website_command(self, args):
        action_map = {
            "collect": self._website_collect,
            "clean": self._website_clean,
            "process": self._website_process,
        }
        action = args.action
        if action in action_map:
            action_map[action](args)

    def _website_collect(self, args):
        collect(args.url, args.auth_header, args.target_only)
        print("Collection completed.")

    def _website_clean(self, args):
        clean_data()

    def _website_process(self, args):
        from website_processor import DataProcessor
        processor = DataProcessor()

        if args.subdomains:
            [print(subdomain) for subdomain in get_subdomains()]

        if args.emails:
            emails = processor.get_emails(DATA_DIR)
            [print(email) for email in get_emails()]
            print(f"Extracted Emails: {emails}")

        if args.pdfs:
            pdf_texts = processor.get_pdfs(DATA_DIR)
            print("Extracted PDF Texts:")
            for pdf_text in pdf_texts:
                print(pdf_text)

        if args.keywords:
            keywords_result = processor.find_keywords(DATA_DIR, args.keywords)
            print(f"Keywords found in collected data: {keywords_result}")

    def _handle_file_command(self, args):
        """ Handle file-related commands """
        action_map = {
            "process": self._file_process,
        }
        action = args.action
        if action in action_map:
            action_map[action](args)

    def _file_process(self, args):
        from website_processor import DataProcessor
        processor = DataProcessor()

        if os.path.exists(args.filepath):
            if args.emails:
                emails = processor.get_emails_from_file(args.filepath)
                print(f"Extracted Emails: {emails}")

            if args.pdfs:
                pdf_text = processor.get_pdf_text(args.filepath)
                print("Extracted PDF Text:")
                print(pdf_text)

            if args.keywords:
                keywords_result = processor.find_keywords_in_file(args.filepath, args.keywords)
                print(f"Keywords found in file: {keywords_result}")
        else:
            print(f"File {args.filepath} does not exist.")

    def _handle_telegram_command(self, args):
        """ Handle Telegram-related commands """
        try:
            identity_name = get_first_telegram_identity(self.auth_service)
        except ValueError as e:
            print(e)
            return

        telegram_service = TelegramService(self.auth_service, identity_name)

        action_map = {
            "collect": self._telegram_collect,
            "process": self._telegram_process,
        }
        action = args.action
        if action in action_map:
            action_map[action](args, telegram_service)

    def _telegram_collect(self, args, telegram_service):
        if args.channels:
            telegram_service.collect_channels()
            print("Collected all channels.")

        if args.users:
            if args.channel:
                telegram_service.collect_users_in_channel(args.channel)
                print(f"Collected users from channel: {args.channel}")
            else:
                print("Please provide a channel using --channel.")

        if args.messages:
            if args.channel:
                telegram_service.collect_messages_from_channel(args.channel)
                print(f"Collected messages from channel: {args.channel}")
            else:
                print("Please provide a channel using --channel.")

    def _telegram_process(self, args, telegram_service):
        if args.user_interactions:
            if args.channel:
                interactions = telegram_service.process_user_interactions(args.channel)
                print(f"User interactions in channel {args.channel}:")
                for interaction in interactions:
                    print(interaction)
            else:
                print("Please provide a channel using --channel.")

        if args.keywords:
            if args.channel:
                keyword_analysis = telegram_service.analyze_keywords_in_messages(args.keywords, args.channel)
                print(f"Keywords found in channel {args.channel}: {keyword_analysis}")
            else:
                print("Please provide a channel using --channel.")
