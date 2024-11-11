import os
import re
import json 

def extract_emails_from_text(text):
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    return set(re.findall(email_pattern, text))

def extract_emails_from_file(file_path):
    emails = set()
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()
                emails.update(extract_emails_from_text(content))
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
    else:
        print(f"File {file_path} not found.")
    return emails

def extract_emails_from_directory(directory):
    emails = set()
    if os.path.exists(directory):
        for root, _, files in os.walk(directory):
            for filename in files:
                file_path = os.path.join(root, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                        content = file.read()
                        emails.update(extract_emails_from_text(content))
                except Exception as e:
                    print(f"Failed to read {file_path}: {e}")
    else:
        print(f"Directory {directory} not found.")
    return emails

def get_all_emails(links_file, data_dir):
    emails = extract_emails_from_file(links_file)
    emails.update(extract_emails_from_directory(data_dir))
    return emails

FILE_EXTENSIONS = [
    "pdf", "jpeg", "webp", "dat", "sql", "webm", "bin", "docx", "doc", "pptx",
    "xlsx", "jpg", "png", "txt", "bak", "backup", "xls", "csv", "md", "cpp", "py"
]

def extract_files_from_links(link_file):
    file_links = []
    if os.path.exists(link_file):
        with open(link_file, 'r', encoding='utf-8') as f:
            links = json.load(f)
            for url, details in links.items():
                if any(url.lower().endswith(f".{ext}") for ext in FILE_EXTENSIONS):
                    file_links.append(url)
    return file_links

def process_files_for_extension(links_file):
    file_links = extract_files_from_links(links_file)
    
    if file_links:
        print(f"Found {len(file_links)} files with matching extensions:")
        for file in file_links:
            print(file)
    else:
        print("No files found with matching extensions.")
