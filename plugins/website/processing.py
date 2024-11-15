import os
import re
import shutil
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from techka_rust_bindings import DataProcessor

SCRAPED_DIR = "data/output/scraped"

def load_tlds(tld_file_path):
    tlds = set()
    if os.path.exists(tld_file_path):
        with open(tld_file_path, 'r') as f:
            for line in f:
                tlds.add(line.strip().lower())
    return tlds

def get_pdfs(data_dir):
    processor = DataProcessor()
    return processor.get_pdfs(data_dir)

def get_emails(data_dir):
    processor = DataProcessor()
    emails = []

    all_urls_path = "data/output/all_urls.txt"
    if os.path.exists(all_urls_path):
        with open(all_urls_path) as f:
            for entry in f:
                if "mailto" in entry:
                    emails.append(entry.split("mailto:")[1].strip())

    emails.extend(processor.get_emails(data_dir))
    return set(emails)

def get_keywords(data_dir, keywords):
    processor = DataProcessor()
    return processor.find_keywords(data_dir, keywords)

def clean_data(data_dir):
    if os.path.exists(data_dir):
        shutil.rmtree(data_dir)
        print("Scraped data has been removed.")
    else:
        print("No data to clean.")

def extract_subdomains_from_collected_data(scraped_dir, tlds):
    subdomains = set()
    processor = DataProcessor()

    for root, _, files in os.walk(scraped_dir):
        for file in files:
            file_path = os.path.join(root, file)
            if file.lower().endswith('.pdf'):
                pdf_text = processor.get_pdf_text(file_path)
                subdomains.update(extract_valid_subdomains_from_text(pdf_text, tlds))
            elif file.lower().endswith(('.html', '.htm', '.txt')):
                subdomains.update(extract_subdomains_from_html_or_text(file_path, tlds))

    return subdomains

def extract_subdomains_from_html_or_text(file_path, tlds):
    subdomains = set()
    url_pattern = re.compile(r'https?://(?:www\.)?([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})')

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if file_path.lower().endswith(('.html', '.htm')):
                soup = BeautifulSoup(content, 'html.parser')
                urls = [a['href'] for a in soup.find_all('a', href=True)]
                urls += [link['src'] for link in soup.find_all(src=True)]
                content += " ".join(urls)

            matches = url_pattern.findall(content)
            for match in matches:
                parsed_subdomain = urlparse("https://" + match).netloc
                if is_valid_subdomain(parsed_subdomain, tlds):
                    subdomains.add(parsed_subdomain.strip())
    except Exception as e:
        print(f"Error reading {file_path}: {e}")

    return subdomains

def extract_valid_subdomains_from_text(text, tlds):
    subdomains = set()
    domain_pattern = re.compile(r'\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\b')

    matches = domain_pattern.findall(text)
    for match in matches:
        parsed_subdomain = urlparse("https://" + match).netloc
        if is_valid_subdomain(parsed_subdomain, tlds):
            subdomains.add(parsed_subdomain.strip())

    return subdomains

def is_valid_subdomain(domain, tlds):
    parts = domain.rsplit('.', 2)
    return len(parts) > 1 and parts[-1].lower() in tlds

def get_domains(data_dir, tld_file):
    tlds = load_tlds(tld_file)
    return extract_subdomains_from_collected_data(data_dir, tlds)
