import argparse
import sys
from core.cli.help import print_full_help
from core.cli.last_usage import check_last_usage
from core.cli.logo import logo

class CliController:
    def __init__(self, plugins):
        self.parser = argparse.ArgumentParser(
            description="SOCMINT C4ISR - surveillance and reconnaissance."
        )
        
        self.parser.add_argument(
            '--full-help', action='store_true', help="Show full help message for all commands and exit"
        )
        
        self.subparsers = self.parser.add_subparsers(dest="command", required=True)
        
        self.command_map = {}
        
        for plugin in plugins:
            plugin.register_commands(self.subparsers)
            plugin_command = plugin.registered_as
            self.command_map[plugin_command] = plugin.handle

    def execute(self, args=None):
        if check_last_usage():
            print(logo())
            
        if args is None:
            args = sys.argv[1:]
        
        if '--full-help' in args:
            print_full_help(argparse, self.parser, self.subparsers)
            sys.exit(0)

        parsed_args = self.parser.parse_args(args)
        
        if parsed_args.command in self.command_map:
            self.command_map[parsed_args.command](parsed_args)
        else:
            print(f"Unknown command: {parsed_args.command}")