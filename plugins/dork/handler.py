import os
from core.cli.colors import GREEN, RED, RESET, YELLOW
from plugins.plugin_base import Plugin
from plugins.dork.services.dorking import Dorking
from plugins.dork.processing import get_all_emails, extract_files_from_links
from plugins.website.processing import clean_data, get_keywords

DATA_DIR = "data/dorking_output/"
LINKS_FILE = "data/dorking_output/collected_links.json"
DORKS_FILE = "plugins/dork/cool_dorks.txt"
FILE_EXTENSIONS = ["pdf", "jpeg", "webp", "dat", "sql", "webm", "bin", "docx", "doc", "pptx", "xlsx", "jpg", "png", "txt", "bak", "backup", "xls", "csv", "md", "cpp", "py"]

class Handler(Plugin):
    def register_as(self):
        return "dork"
    
    def commands(self, subparsers):
        dorking_parser = subparsers.add_parser(self.register_as(), help="Dorking-related commands")
        dorking_subparsers = dorking_parser.add_subparsers(dest="action", required=True)
        
        dorking_subparsers.add_parser("dorks", help="Show dorks")

        collect_parser = dorking_subparsers.add_parser("collect", help="Collect data using dorking")
        collect_parser.add_argument("query", type=str, help="Dorking query")
        collect_parser.add_argument("--download", action="store_true", help="Download content of collected links", required=False)
        collect_parser.add_argument("--slow-search", action="store_true", help="Enable slower search", required=False)
        collect_parser.add_argument("--max-pages", type=int, help="Limit on pages to collect", required=False, default=100)

        dorking_subparsers.add_parser("clean", help="Remove all collected data")

        process_parser = dorking_subparsers.add_parser("process", help="Process collected data")
        process_parser.add_argument("--emails", action="store_true", help="Extract emails from collected data")
        process_parser.add_argument("--keywords", nargs="+", help="Search for specific keywords in collected data")
        process_parser.add_argument("--files", action="store_true", help="Extract files from collected links based on extensions")

    def handle(self, args):
        action_map = {
            "collect": self._handle_collect,
            "clean": self._handle_clean,
            "process": self._handle_process,
        }
        action = args.action
        if action in action_map:
            action_map[action](args)
        else:
            self.print_cool_dorks()

    def _handle_collect(self, args):
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
            
        dorker = Dorking(
            output_dir=DATA_DIR, 
            max_pages=args.max_pages, 
            link_file=LINKS_FILE,
            slow_search=args.slow_search, 
            no_download=not args.download
        )
        dorker.run(args.query)
        print("Data collection completed.")

    def _handle_clean(self, args):
        clean_data(DATA_DIR)
        print("Collected data has been cleaned.")

    def _handle_process(self, args):
        if args.emails:
            emails = get_all_emails(LINKS_FILE, DATA_DIR)
            for email in emails:
                print(email)

        if args.keywords:
            keywords = get_keywords(DATA_DIR, args.keywords)
            for _1, _2, _3 in keywords:
                colored_match = _3
                for keyword in args.keywords:
                    colored_match = colored_match.replace(keyword, f"{RED}{keyword}{RESET}")
                print(f"[{YELLOW}{_1}{RESET}: {GREEN}{_2}{RESET}] {colored_match}")

        if args.files:
            files = extract_files_from_links(LINKS_FILE)
            for file_url in files:
                print(file_url)

    def print_cool_dorks(self):
        if os.path.exists(DORKS_FILE):
            with open(DORKS_FILE, "r") as file:
                dorks = file.readlines()

            print("Cool Dorks:")
            for dork in dorks:
                print(dork.strip())
        else:
            print(f"No dorks file found at {DORKS_FILE}. Please create it and add dorks.")
