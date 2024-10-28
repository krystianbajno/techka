import os

class FileHandler:
    def init_commands(self, subparsers):
        file_parser = subparsers.add_parser("file", help="File related commands")
        file_subparsers = file_parser.add_subparsers(dest="action", required=True)

        file_process_parser = file_subparsers.add_parser("process", help="Process a file")
        file_process_parser.add_argument("filepath", type=str, help="Path to the file to process")
        file_process_parser.add_argument("--emails", action="store_true", help="Extract emails from the file (includes PDFs)")
        file_process_parser.add_argument("--pdfs", action="store_true", help="Extract and print text from PDFs and documents")
        file_process_parser.add_argument("--keywords", nargs="+", help="List of keywords to search for (includes PDFs)")

    def handle(self, args):
        action_map = {
            "process": self._file_process,
        }
        action = args.action
        if action in action_map:
            action_map[action](args)

    def _file_process(self, args):
        from website_processor import DataProcessor
        processor = DataProcessor()

        if os.path.exists(args.filepath):
            if args.emails:
                emails = processor.get_emails_from_file(args.filepath)
                print(f"Extracted Emails: {emails}")

            if args.pdfs:
                pdf_text = processor.get_pdf_text(args.filepath)
                print("Extracted PDF Text:")
                print(pdf_text)

            if args.keywords:
                keywords_result = processor.find_keywords_in_file(args.filepath, args.keywords)
                print(f"Keywords found in file: {keywords_result}")
        else:
            print(f"File {args.filepath} does not exist.")
