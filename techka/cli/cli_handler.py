import argparse
from techka.auth.auth_service import AuthService
from techka.cli.last_usage import check_last_usage
from techka.cli.website_handler import WebsiteHandler
from techka.cli.file_handler import FileHandler
from techka.cli.telegram_handler import TelegramHandler
from techka.cli.logo import logo


class CliHandler:
    def __init__(self):
        self.auth_service = AuthService()
        self.parser = argparse.ArgumentParser(description="SOCMINT C4ISR - surveillance and reconnaissance.")
        self.subparsers = self.parser.add_subparsers(dest="command", required=True)

        self.website_handler = WebsiteHandler()
        self.file_handler = FileHandler()
        self.telegram_handler = TelegramHandler(self.auth_service)

        self._init_website_commands()
        self._init_file_commands()
        self._init_telegram_commands()

        self.command_map = {
            "website": self.website_handler.handle,
            "file": self.file_handler.handle,
            "telegram": self.telegram_handler.handle,
        }

    def _init_website_commands(self):
        self.website_handler.init_commands(self.subparsers)

    def _init_file_commands(self):
        self.file_handler.init_commands(self.subparsers)

    def _init_telegram_commands(self):
        self.telegram_handler.init_commands(self.subparsers)

    def execute(self, args=None):
        # Check last usage and display logo if needed
        if check_last_usage():
            print(logo())

        # Parse and execute command
        parsed_args = self.parser.parse_args(args)
        command = parsed_args.command
        if command in self.command_map:
            self.command_map[command](parsed_args)
        else:
            print(f"Unknown command: {command}")

