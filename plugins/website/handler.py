from plugins.plugin_base import Plugin
from plugins.website.collect import collect
from plugins.website.processing import clean_data, get_emails, get_keywords, get_pdfs, get_subdomains

DATA_DIR = "data/output"
ALL_URLS_FILE = "data/output/all_urls.txt"

class Handler(Plugin):
    def register_as(self):
        return "website"
    
    def commands(self, subparsers):
        website_parser = subparsers.add_parser(self.registered_as, help="Website-related commands")
        website_subparsers = website_parser.add_subparsers(dest="action", required=True)

        collect_parser = website_subparsers.add_parser("collect", help="Collect data from a website")
        collect_parser.add_argument("url", type=str, help="Target URL")
        collect_parser.add_argument("--slow-download", action="store_true", help="Enable slower download", required=False)
        collect_parser.add_argument("--max-pages", type=int, help="Limit on pages to collect", required=False, default=200)
        collect_parser.add_argument("--auth-header", type=str, help="Auth header in 'Key=Value' format", required=False)
        collect_parser.add_argument("--target-only", action="store_true", help="Limit to target domain only", required=False)
        collect_parser.add_argument("--techkagoofil", action="store_true", help="Passively find documents using dorks and public search engines", required=False)
        collect_parser.add_argument("--scrap", action="store_true", help="Clone website and save", required=False)

        website_subparsers.add_parser("clean", help="Remove all collected data")

        process_parser = website_subparsers.add_parser("process", help="Process collected data")
        process_parser.add_argument("--subdomains", action="store_true", help="Extract subdomains")
        process_parser.add_argument("--emails", action="store_true", help="Extract emails from collected data")
        process_parser.add_argument("--pdfs", action="store_true", help="Extract text from PDFs")
        process_parser.add_argument("--keywords", nargs="+", help="Search for specific keywords in collected data")
        
        return "website"
    
    def handle(self, args):
        action_map = {
            "collect": self._handle_collect,
            "clean": self._handle_clean,
            "process": self._handle_process,
        }
        action = args.action
        if action in action_map:
            action_map[action](args)

    def _handle_collect(self, args):
        collect(
            args.url, 
            scrap=args.scrap,
            auth_header=args.auth_header, 
            target_only=args.target_only, 
            slow_download=args.slow_download, 
            max_pages=args.max_pages, 
            techkagoofil=args.techkagoofil
        )
        
        print("Data collection completed.")

    def _handle_clean(self, args):
        clean_data(DATA_DIR)
        print("Collected data has been cleaned.")

    def _handle_process(self, args):
        if args.subdomains:
            subdomains = get_subdomains(ALL_URLS_FILE)
            for subdomain in subdomains:
                print(subdomain)

        if args.emails:
            emails = get_emails(DATA_DIR)
            for email in emails:
                print(email)

        if args.pdfs:
            pdf_texts = get_pdfs(DATA_DIR)
            for pdf_text in pdf_texts:
                print(pdf_text)

        if args.keywords:
            keywords = get_keywords(DATA_DIR, args.keywords)
            print(keywords)
