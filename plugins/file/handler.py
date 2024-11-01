import os

from plugins.file.processing import get_emails, get_keywords, get_pdfs
from plugins.plugin_base import Plugin

class Handler(Plugin):
    def init_commands(self, subparsers):
        file_parser = subparsers.add_parser("file", help="File related commands")
        file_subparsers = file_parser.add_subparsers(dest="action", required=True)

        file_process_parser = file_subparsers.add_parser("process", help="Process a file")
        file_process_parser.add_argument("filepath", type=str, help="Path to the file to process")
        file_process_parser.add_argument("--emails", action="store_true", help="Extract emails from the file (includes PDFs)")
        file_process_parser.add_argument("--pdfs", action="store_true", help="Extract and print text from PDFs and documents")
        file_process_parser.add_argument("--keywords", nargs="+", help="List of keywords to search for (includes PDFs)")

    def register_as(self):
        return "file"
        
    def handle(self, args):
        action_map = {
            "process": self._file_process,
        }
        action = args.action
        if action in action_map:
            action_map[action](args)

    def _file_process(self, args):
        if os.path.exists(args.filepath):
            if args.emails:
                for email in get_emails(args.filepath):
                    print(email) 

            if args.pdfs:
                for pdf_text in get_pdfs(args.filepath):
                    print(pdf_text)

            if args.keywords:
                print(get_keywords(args.filepath, args.keywords))
        else:
            print(f"File {args.filepath} does not exist.")
