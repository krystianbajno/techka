from abc import ABC
from core.providers.service_provider import ServiceProvider

class Plugin(ABC):
    def __init__(self, service_provider: ServiceProvider):
        self.service_provider = service_provider
        
    def register_as(self):
        return "override_return_name_of_your_plugin"
    
    def initialize_commands(self, subparsers):
        self.init_commands(subparsers)
        return self.register_as()
        
    def init_commands(self, subparsers):
        parser = subparsers.add_parser("sample", help="Sample plugin command")
        parser.add_argument("--example", type=str, help="Example argument")

    def handle(self, args):
        print(f"Sample Plugin: handling command with argument {args.example}")
