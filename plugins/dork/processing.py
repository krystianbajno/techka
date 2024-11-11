import os
import re

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
