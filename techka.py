import argparse
import os
import shutil
from website.collect import collect
from website.processing import get_emails, get_subdomains

DATA_DIR = "data/output"

def clean_data():
    if os.path.exists(DATA_DIR):
        shutil.rmtree(DATA_DIR)
        print("Scraped data has been removed.")
    else:
        print("No data to clean.")

def main():
    parser = argparse.ArgumentParser(description="Data collector and processor")
    subparsers = parser.add_subparsers(dest="command", required=True)

    website_parser = subparsers.add_parser("website", help="Website related commands")
    website_subparsers = website_parser.add_subparsers(dest="action", required=True)

    collect_parser = website_subparsers.add_parser("collect", help="Collect data from a website")
    collect_parser.add_argument("url", type=str, help="The target URL")
    collect_parser.add_argument("--auth-header", type=str, help="Authentication header in the format 'Key=Value'", required=False)
    collect_parser.add_argument("--target-only", action="store_true", help="Target only, no subdomains", required=False)

    website_subparsers.add_parser("clean", help="Remove all scraped data")

    process_parser = website_subparsers.add_parser("process", help="Process collected data")
    process_parser.add_argument("--subdomains", action="store_true", help="Extract subdomains")
    process_parser.add_argument("--emails", action="store_true", help="Extract emails from the collected data (includes PDFs)")
    process_parser.add_argument("--pdfs", action="store_true", help="Extract and print text from PDFs and documents")
    process_parser.add_argument("--keywords", nargs="+", help="List of keywords to search for (includes PDFs)")

    file_parser = subparsers.add_parser("file", help="File related commands")
    file_subparsers = file_parser.add_subparsers(dest="action", required=True)

    file_process_parser = file_subparsers.add_parser("process", help="Process a file")
    file_process_parser.add_argument("filepath", type=str, help="Path to the file to process")
    file_process_parser.add_argument("--emails", action="store_true", help="Extract emails from the file (includes PDFs)")
    file_process_parser.add_argument("--pdfs", action="store_true", help="Extract and print text from PDFs and documents")
    file_process_parser.add_argument("--keywords", nargs="+", help="List of keywords to search for (includes PDFs)")

    args = parser.parse_args()

    if args.command == "website":
        if args.action == "collect":
            collect(args.url, args.auth_header, args.target_only)
            print("Collection completed.")

        elif args.action == "clean":
            clean_data()

        elif args.action == "process":
            if args.subdomains:
                [print(subdomain) for subdomain in get_subdomains()]
                
            from website_processor import DataProcessor
            processor = DataProcessor()
            if args.emails:
                [print(email) for email in get_emails()]
                emails = processor.get_emails(DATA_DIR)
                print(f"Extracted Emails: {emails}")

            if args.pdfs:
                pdf_texts = processor.get_pdfs(DATA_DIR)
                print("Extracted PDF Texts:")
                for pdf_text in pdf_texts:
                    print(pdf_text)

            if args.keywords:
                keywords_result = processor.find_keywords(DATA_DIR, args.keywords)
                print(f"Keywords found in collected data: {keywords_result}")

    elif args.command == "file":
        if args.action == "process":
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

if __name__ == "__main__":
    main()
