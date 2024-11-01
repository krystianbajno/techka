import argparse
import importlib
import os
import sys
from techka.auth.auth_service import AuthService
from techka.cli.last_usage import check_last_usage
from techka.cli.logo import logo
import importlib.util

from techka.providers.service_provider import ServiceProvider


class CliHandler:
    def __init__(self):
        self.service_provider = ServiceProvider()
        
        self.parser = argparse.ArgumentParser(
            description="SOCMINT C4ISR - surveillance and reconnaissance."
        )
        
        self.parser.add_argument(
            '--full-help', action='store_true', help="Show full help message for all commands and exit"
        )

        self.subparsers = self.parser.add_subparsers(dest="command", required=True)
        
        self.command_map = {}
        
        self.plugins = self.load_plugins(['plugins'])
        
        for plugin in self.plugins:
            plugin_command = plugin.initialize_commands(self.subparsers)
            self.command_map[plugin_command] = plugin.handle

    def load_module(self, module_name, path):
        spec = importlib.util.spec_from_file_location(module_name, path)
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
            if hasattr(module, "Handler"):
                return module.Handler(self.service_provider)
            else:
                print(f"No Handler class found in {path}")
        except Exception as e:
            print(f"Failed to load handler from {module_name}: {e}")
        return None


    def load_plugins(self, directories):
        plugins = []
        for directory in directories:
            if os.path.exists(directory):
                for plugin_name in os.listdir(directory):
                    plugin_path = os.path.join(directory, plugin_name, 'handler.py')
                    if os.path.isfile(plugin_path):
                        plugin = self.load_module(plugin_name, plugin_path)
                        if plugin:
                            plugins.append(plugin)
        return plugins

    def print_full_help(self):
        """Prints help for all commands and subcommands in a simplified structure."""
        print("\nMain Command Help:\n")
        self.parser.print_help()
        print("\nSubcommand Help:\n")

        for subcommand_name, subparser in self.subparsers.choices.items():
            print(f"\nHelp for '{subcommand_name}' command:")
            subparser.print_help()

            for sub_action in subparser._actions:
                if isinstance(sub_action, argparse._SubParsersAction):
                    for nested_name, nested_subparser in sub_action.choices.items():
                        print(f"\nHelp for '{subcommand_name} {nested_name}' subcommand:")
                        nested_subparser.print_help()

    def execute(self, args=None):
        if check_last_usage():
            print(logo())
            
        if args is None:
            args = sys.argv[1:]
        
        if '--full-help' in args:
            self.print_full_help()
            sys.exit(0)

        parsed_args = self.parser.parse_args(args)
        
        if parsed_args.command in self.command_map:
            self.command_map[parsed_args.command](parsed_args)
        else:
            print(f"Unknown command: {parsed_args.command}")
