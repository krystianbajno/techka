import os
import hashlib
import json
import subprocess
from datetime import datetime
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse, urljoin
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import requests

from techka.website.techkagoofil import TechkaGoofil

OUTPUT_DIR = "data/output"
ALL_URLS_FILE = os.path.join(OUTPUT_DIR, "all_urls.txt")
SCRAPED_DIR = os.path.join(OUTPUT_DIR, "scraped")
METADATA_FILE = os.path.join(OUTPUT_DIR, "metadata.json")
SCRAPING_DEPTH = 5
CONCURRENT_DOWNLOAD_WORKERS = 5

os.makedirs(SCRAPED_DIR, exist_ok=True)

def run_katana_for_urls(target, all_urls_file, auth_header=None, target_only=False):
    katana_cmd = [
        "katana",
        "-jc",
        "-u", target,
        "-d", str(SCRAPING_DEPTH),
        "-headless",
        "-known-files", "all",
        "-mdc", 'status_code == 200',
    ]
    
    if not target_only:
        katana_cmd.extend(["-fs", "fqdn"])
    
    if auth_header:
        key, value = auth_header.split("=", 1)
        katana_cmd.extend(["-H", f"{key}:{value}"])

    try:
        with open(all_urls_file, "w") as f:
            subprocess.run(katana_cmd, stdout=f, check=True)
        print(f"URLs collected and saved in {all_urls_file}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to run katana for URLs: {e}")
        exit(1)

def download_full_page_with_js(url, output_file, auth_header=None):
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            if auth_header:
                key, value = auth_header.split("=", 1)
                page.set_extra_http_headers({key: value})

            page.goto(url)
            page_content = page.content()
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(page_content)
            print(f"Downloaded and saved full content for {url}")
            browser.close()
        except Exception as e:
            print(f"Error parsing {url}: {e}")

def process_url(url, scraped_dir, metadata, collection_date, auth_header=None):
    try:
        parsed_url = urlparse(url)
        path = os.path.join(scraped_dir, parsed_url.netloc, os.path.dirname(parsed_url.path.strip('/')))
        os.makedirs(path, exist_ok=True)

        filename = os.path.basename(parsed_url.path) or "index.html"
        output_file = os.path.join(path, filename)

        if os.path.exists(output_file):
            print(f"Skipping URL as it is already processed: {url}")
            return None

        download_full_page_with_js(url, output_file, auth_header)

        metadata.append({
            "filepath": output_file,
            "url": url,
            "collection_date": collection_date
        })

        return metadata
    
    except Exception as e:
        print(f"Error processing {url}: {e}")
        time.sleep(15)
        return None

def run_playwright_for_content(urls_file, scraped_dir, metadata, auth_header=None):
    with open(urls_file, "r") as f:
        urls = [url.strip() for url in f if url.strip()]

    collection_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    with ThreadPoolExecutor(max_workers=CONCURRENT_DOWNLOAD_WORKERS) as executor:
        futures = [executor.submit(process_url, url, scraped_dir, metadata, collection_date, auth_header) for url in urls]

        for future in as_completed(futures):
            result = future.result()
            if result:
                with open(METADATA_FILE, "w", encoding="utf-8") as json_file:
                    json.dump(metadata, json_file, ensure_ascii=False, indent=4)
                print(f"Metadata saved to {METADATA_FILE}")


def extract_and_download_pdfs(scraped_dir):
    domains = [item for item in os.listdir(scraped_dir) if os.path.isdir(os.path.join(scraped_dir, item)) and '.' in item]

    if not domains:
        print("Error: No domains found in the 'scraped' directory.")
        return

    for domain in domains:
        domain_dir = os.path.join(scraped_dir, domain)

        for root, _, files in os.walk(domain_dir):
            for file in files:
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as html_file:
                    try:
                        soup = BeautifulSoup(html_file, "html.parser")

                        relative_path = os.path.relpath(file_path, os.path.join(scraped_dir))
                        base_url = f"https://{domain}/{os.path.dirname(relative_path)}"

                        pdf_links = [urljoin(base_url, link.get('href')) for link in soup.find_all('a', href=True) if link.get('href').lower().endswith('.pdf')]

                        for pdf_url in pdf_links:
                            parsed_pdf_url = urlparse(pdf_url)
                            if parsed_pdf_url.scheme in ['http', 'https']:
                                output_dir = os.path.join(scraped_dir, parsed_pdf_url.netloc, os.path.dirname(parsed_pdf_url.path.strip('/')))
                                os.makedirs(output_dir, exist_ok=True)
                                download_pdf(pdf_url, output_dir)
                    except Exception as e:
                        print(f"Exception happened while processing file {file_path}: ", e)

def download_pdf(pdf_url, output_dir):
    try:
        response = requests.get(pdf_url, stream=True)
        response.raise_for_status()

        pdf_name = os.path.basename(urlparse(pdf_url).path)
        pdf_path = os.path.join(output_dir, pdf_name)

        with open(pdf_path, "wb") as pdf_file:
            for chunk in response.iter_content(chunk_size=8192):
                pdf_file.write(chunk)

        print(f"Downloaded PDF: {pdf_name} to {output_dir}")

    except Exception as e:
        print(f"Error downloading PDF from {pdf_url}: {e}")
        
def hash_url(url):
    return hashlib.md5(url.encode()).hexdigest()

def run_techkagoofil(domain, save_directory):
    print(f"[*] Running TechkaGoofil for domain: {domain}")
    urls_out_path = os.path.join(OUTPUT_DIR, f"techkagoofil_urls_{domain}.txt")
    output_json_path = os.path.join(OUTPUT_DIR, f"techkagoofil_filebindings_{domain}.txt")

    techkagoofil = TechkaGoofil(
        domain=domain,
        output_dir=save_directory
    )
    links, file_metadata = techkagoofil.run()
    
    with open(output_json_path, "w") as f:
        json.dump(file_metadata, f, indent=4)
        print(f"+ Metadata saved to {output_json_path}")
    
    with open(urls_out_path, "w") as f:
        f.write("\n".join(links))
        print(f"+ Links saved to {urls_out_path}")

def collect(target, auth_header=None, target_only=False):
    METADATA = []

    if os.path.exists(ALL_URLS_FILE):
        choice = input(f"{ALL_URLS_FILE} exists. Do you want to start over and run katana again to collect URLs? (y/n): ")
        if choice.lower() == 'y':
            os.remove(ALL_URLS_FILE)
            run_katana_for_urls(target, ALL_URLS_FILE, auth_header, target_only)
        else:
            print(f"Using existing URLs from {ALL_URLS_FILE}")
    else:
        run_katana_for_urls(target, ALL_URLS_FILE, auth_header, target_only)

    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, "r") as metadata_file:
            METADATA = json.loads(metadata_file.read())

    run_playwright_for_content(ALL_URLS_FILE, SCRAPED_DIR, METADATA, auth_header)
    
    extract_and_download_pdfs(SCRAPED_DIR)
    
    run_techkagoofil(target, os.path.join(os.path.join(SCRAPED_DIR, target), "techkagoofil"))

    print("Finished")
