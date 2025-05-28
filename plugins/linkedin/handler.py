from core.cli.colors import GREEN, RESET, YELLOW
from plugins.plugin_base import Plugin

class Handler(Plugin):
    def register_as(self):
        return "linkedin"
    
    def commands(self, subparsers):
        linkedin_parser = subparsers.add_parser(self.registered_as, help="Telegram related commands")
            
    def handle(self, args):
        print(f"[LINKEDIN] Use{GREEN} techka/plugins/linkedin/scripts{RESET} directory and paste into devtools. :){RESET}\n{YELLOW}The LinkedIn service is made of javascript.{RESET}")