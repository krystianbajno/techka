import os
import json
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from typing import List

class Downloader:
    def __init__(self, output_dir, link_file):
        self.output_dir = output_dir
        self.link_file = link_file

    def download_collected_links(self):
        links = self.load_links_from_json()
        if not links:
            print(f"No collected links file found at {self.link_file}. Skipping download.")
            return

        urls = [url for url in links.keys()]
        print(f"Starting download of {len(urls)} links...")

        self.download_urls(urls)

    def download_urls(self, urls: List[str]):
        os.makedirs(self.output_dir, exist_ok=True)

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            for url in urls:
                try:
                    output_file = os.path.join(self.output_dir, self._sanitize_filename(url))
                    print(f"Downloading content from {url}...")

                    page.goto(url, timeout=60000)
                    
                    with open(output_file, "w", encoding="utf-8") as f:
                        f.write(page.content())

                    print(f"Downloaded content for {url} to {output_file}")

                except PlaywrightTimeoutError:
                    print(f"Timeout error fetching {url}")
                except Exception as e:
                    print(f"Error fetching {url}: {e}")
                finally:
                    page.close()
                    page = browser.new_page()

            browser.close()

    def _sanitize_filename(self, url):
        sanitized = url.replace("http://", "").replace("https://", "").replace("/", "_").replace("?", "_").replace("&", "_")
        return sanitized[:255] + ".html"

    def load_links_from_json(self):
        if os.path.exists(self.link_file):
            with open(self.link_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def save_links_to_json(self, links):
        os.makedirs(os.path.dirname(self.link_file), exist_ok=True)
        with open(self.link_file, 'w', encoding='utf-8') as f:
            json.dump(links, f, ensure_ascii=False, indent=4)
