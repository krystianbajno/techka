import argparse
import sys
from techka.auth.auth_service import AuthService
from techka.cli.last_usage import check_last_usage
from techka.cli.website_handler import WebsiteHandler
from techka.cli.file_handler import FileHandler
from techka.cli.telegram_handler import TelegramHandler
from techka.cli.logo import logo


class CliHandler:
    def __init__(self):
        self.auth_service = AuthService()
        
        # Main parser with normal help enabled
        self.parser = argparse.ArgumentParser(
            description="SOCMINT C4ISR - surveillance and reconnaissance."
        )
        
        # Add `--full-help` option separately
        self.parser.add_argument(
            '--full-help', action='store_true', help="Show full help message for all commands and exit"
        )

        # Set up subparsers
        self.subparsers = self.parser.add_subparsers(dest="command", required=True)
        
        # Initialize handlers and their subcommands
        self.website_handler = WebsiteHandler()
        self.file_handler = FileHandler()
        self.telegram_handler = TelegramHandler(self.auth_service)
        self._init_website_commands()
        self._init_file_commands()
        self._init_telegram_commands()

        # Map commands to handler functions
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
        if check_last_usage():
            print(logo())
        # Check if --full-help was provided without other args
        if args is None:
            args = sys.argv[1:]
        
        # Show full help if `--full-help` is in args
        if '--full-help' in args:
            self.print_full_help()
            sys.exit(0)

        # Parse and execute command as normal
        parsed_args = self.parser.parse_args(args)
        if parsed_args.command in self.command_map:
            self.command_map[parsed_args.command](parsed_args)
        else:
            print(f"Unknown command: {parsed_args.command}")

    def print_full_help(self):
        """Prints help for all commands and subcommands in a simplified structure."""
        print("\nMain Command Help:\n")
        self.parser.print_help()
        print("\nSubcommand Help:\n")

        # Iterate over each primary subcommand in subparsers
        for subcommand_name, subparser in self.subparsers.choices.items():
            print(f"\nHelp for '{subcommand_name}' command:")
            subparser.print_help()

            # Check for nested subparsers within each primary subcommand
            for sub_action in subparser._actions:
                if isinstance(sub_action, argparse._SubParsersAction):
                    for nested_name, nested_subparser in sub_action.choices.items():
                        print(f"\nHelp for '{subcommand_name} {nested_name}' subcommand:")
                        nested_subparser.print_help()
