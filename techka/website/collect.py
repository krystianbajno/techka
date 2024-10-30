import logging
import os
import json
import subprocess
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse, urljoin
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from techka.website.techkagoofil import TechkaGoofil

OUTPUT_DIR = "data/output"
ALL_URLS_FILE = os.path.join(OUTPUT_DIR, "all_urls.txt")
SCRAPED_DIR = os.path.join(OUTPUT_DIR, "scraped")
METADATA_FILE = os.path.join(OUTPUT_DIR, "metadata.json")
SCRAPING_DEPTH = 10
CONCURRENT_DOWNLOAD_WORKERS = 5

os.makedirs(SCRAPED_DIR, exist_ok=True)

def run_katana_for_urls(target, all_urls_file, auth_header=None, target_only=False):
    logger = logging.getLogger("KatanaLogger")
    logger.setLevel(logging.INFO)
    
    file_handler = logging.FileHandler(all_urls_file)
    file_handler.setLevel(logging.INFO)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(asctime)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    katana_cmd = [
        "katana",  "-u", target, "-d", str(SCRAPING_DEPTH), "-jsluice", "-js-crawl",
        "-headless", "-kf", "robotstxt,sitemapxml", "-mdc", 'status_code == 200'
    ]
    if target_only:
        katana_cmd.extend(["-fs", "fqdn"])
    if auth_header:
        key, value = auth_header.split("=", 1)
        katana_cmd.extend(["-H", f"{key}:{value}"])

    try:
        process = subprocess.Popen(katana_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
        
        for line in iter(process.stdout.readline, ''):
            logger.info(line.strip())

        process.stdout.close()
        process.wait()

        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, katana_cmd)
    finally:
        logger.removeHandler(file_handler)
        logger.removeHandler(console_handler)
        

def download_full_page_with_js(url, output_file, auth_header=None):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        if auth_header:
            key, value = auth_header.split("=", 1)
            page.set_extra_http_headers({key: value})

        try:
            page.goto(url)
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(page.content())
            print(f"Downloaded content for {url}")
        except Exception as e:
            print(f"Error fetching {url}: {e}")
        finally:
            browser.close()

def process_url(url, scraped_dir, metadata, collection_date, auth_header=None):
    parsed_url = urlparse(url)
    
    path = os.path.join(scraped_dir, parsed_url.netloc, parsed_url.path.strip('/'))
    
    if parsed_url.path.endswith('/') or not os.path.basename(parsed_url.path):
        os.makedirs(path, exist_ok=True)
        output_file = os.path.join(path, "index.html")
    else:
        directory = os.path.dirname(path)
        os.makedirs(directory, exist_ok=True)
        filename = os.path.basename(parsed_url.path)
        if '.' not in filename:
            filename += ".html" 
        output_file = os.path.join(directory, filename)

    if os.path.exists(output_file):
        print(f"Skipping {url}; already processed.")
        return

    download_full_page_with_js(url, output_file, auth_header)
    
    metadata_entry = {
        "filepath": output_file,
        "url": url,
        "collection_date": collection_date
    }
    metadata.append(metadata_entry)

def run_playwright_for_content(urls_file, scraped_dir, metadata, auth_header=None):
    if not os.path.exists(urls_file):
        os.makedirs(os.path.dirname(urls_file), exist_ok=True)
        open(urls_file, "w").close()

    with open(urls_file, "r") as f:
        urls = [url.strip() for url in f if url.strip()]

    collection_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with ThreadPoolExecutor(max_workers=CONCURRENT_DOWNLOAD_WORKERS) as executor:
        futures = [executor.submit(process_url, url, scraped_dir, metadata, collection_date, auth_header) for url in urls]
        for future in as_completed(futures):
            future.result()

    with open(METADATA_FILE, "w", encoding="utf-8") as json_file:
        json.dump(metadata, json_file, ensure_ascii=False, indent=4)
    print(f"Metadata saved to {METADATA_FILE}")


def extract_and_download_files(scraped_dir, file_extensions):
    for domain in (d for d in os.listdir(scraped_dir) if os.path.isdir(os.path.join(scraped_dir, d))):
        for root, _, files in os.walk(os.path.join(scraped_dir, domain)):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as html_file:
                        soup = BeautifulSoup(html_file, "html.parser")
                        base_url = f"https://{domain}/" + os.path.relpath(root, os.path.join(scraped_dir, domain)).replace("\\", "/") + "/"
                        
                        file_links = [
                            urljoin(base_url, link.get('href')) for link in soup.find_all('a', href=True)
                            if any(link.get('href').endswith(f'.{ext}') for ext in file_extensions)
                        ]
                        for file_url in file_links:
                            download_file(file_url, os.path.join(root))  
                except Exception as e:
                    print(f"Error occurred with {file_path} - {e}")

def download_file(file_url, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    try:
        response = requests.get(file_url, stream=True)
        response.raise_for_status()
        file_name = os.path.basename(file_url)
        with open(os.path.join(output_dir, file_name), "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"Downloaded file: {file_name}")
    except requests.HTTPError as e:
        print(f"File download error from {file_url}: {e}")
        
def run_techkagoofil(domain, save_directory, slow_download=False, max_pages=200):
    print(f"[*] Running TechkaGoofil for domain: {domain}")
    link_file = os.path.join(OUTPUT_DIR, f"techkagoofil_urls_{domain}.txt")
    output_json_path = os.path.join(OUTPUT_DIR, f"techkagoofil_filebindings_{domain}.json")

    techkagoofil = TechkaGoofil(
        domain=domain,
        output_dir=save_directory,
        slow_download=slow_download,
        link_file=link_file,
        max_pages=max_pages
    )

    try:
        _, file_metadata = techkagoofil.run()

        with open(output_json_path, "w", encoding="utf-8") as json_file:
            json.dump(file_metadata, json_file, indent=4)
            print(f"+ Metadata saved to {output_json_path}")

        print(f"+ Links saved to {link_file}")

    except Exception as e:
        print(f"Error running TechkaGoofil for domain {domain}: {e}")

def collect(target, auth_header=None, target_only=False, slow_download=False, techkagoofil=False, scrap=False, max_pages=200):
    
    if scrap:
        metadata = []
            
        if not os.path.exists(ALL_URLS_FILE) \
            or (os.path.exists(ALL_URLS_FILE) \
                and input(f"{ALL_URLS_FILE} exists. Re-run Katana? (y/n): ").strip().lower() == 'y'):
                
            run_katana_for_urls(target, ALL_URLS_FILE, auth_header, target_only)

        if os.path.exists(METADATA_FILE):
            with open(METADATA_FILE, "r") as metadata_file:
                metadata = json.load(metadata_file)

        run_playwright_for_content(ALL_URLS_FILE, SCRAPED_DIR, metadata, auth_header)
        
        extract_and_download_files(SCRAPED_DIR, ["pdf", "jpeg", "webp", "dat", "sql" "webm", "bin", "docx", "doc", "pptx", "xlsx", "jpg", "png", "txt", "bak", "backup", "xls", "csv", "md", "cpp", "py", "js"])

        with open(METADATA_FILE, "w", encoding="utf-8") as json_file:
            json.dump(metadata, json_file, ensure_ascii=False, indent=4)
        
    if techkagoofil:
        run_techkagoofil(target, os.path.join(SCRAPED_DIR, target, "techkagoofil"), slow_download=slow_download, max_pages=max_pages)
        
    print("Collection finished.")