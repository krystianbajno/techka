import os
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

class Downloader:
    def __init__(self, output_dir, link_file):
        self.output_dir = output_dir
        self.link_file = link_file

    def download_collected_links(self):
        if not os.path.exists(self.link_file):
            print(f"No collected links file found at {self.link_file}. Skipping download.")
            return

        with open(self.link_file, "r") as f:
            links = [line.strip().split("\t")[0] for line in f]

        print(f"Starting download of {len(links)} links...")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            for url in links:
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
