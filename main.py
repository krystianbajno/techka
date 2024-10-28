from techka.cli.logo import logo
from techka.cli.cli_handler import CliHandler

if __name__ == "__main__":
    print(logo())
    cli_handler = CliHandler()
    cli_handler.execute()
