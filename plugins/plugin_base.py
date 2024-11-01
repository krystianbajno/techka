from abc import ABC

from core.providers.service_provider import ServiceProvider

class Plugin(ABC):
    def __init__(self, core_dependencies):
        f"""
        Sets dependencies as attributes of plugin
        Dependencies:
          service_provider: {ServiceProvider} contains core services for use in plugins
        """
        
        """Set from register_as, used for parser commands and registration"""
        self.registered_as: str = "" 

        for key, value in core_dependencies.items():
            setattr(self, key, value)
            
        self.initialize()
        
    def initialize(self):
        """
        Initialize your plugin here
        """
        pass

    def register_as(self):
        """
        Return name of the plugin eg 'telegram', should be same as parser name.
        """
        return "not_registered"
    
    def commands(self, subparsers):
        """
          Implement subparsers.add_parser here
          parser = subparsers.add_parser(self.REGISTERED_AS, help="Sample plugin command")
          parser.add_argument("--example", type=str, help="Example argument")
        """
        raise NotImplementedError

    def handle(self, args):
        """Gets arguments from argparse and handle commands"""
        raise NotImplementedError
        
    def register_commands(self, subparsers):
        """Register commands"""
        self.registered_as = self.register_as()
        self.commands(subparsers)
