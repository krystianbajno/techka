import os
import time
from urllib.parse import urljoin, urlparse
from playwright.sync_api import sync_playwright
from concurrent.futures import ThreadPoolExecutor
import requests
from bs4 import BeautifulSoup

class TechkaGoofil:
    def __init__(self, domain, output_dir="output", file_types=["pdf"]):
        self.domain = domain
        self.output_dir = output_dir
        self.file_types = file_types
        self.seen_urls = set()
        os.makedirs(self.output_dir, exist_ok=True)

    def start_browser(self):
        """Start the browser session once for all engines."""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=False)
        self.page = self.browser.new_page()

    def close_browser(self):
        """Close the browser session."""
        self.browser.close()
        self.playwright.stop()

    def accept_cookies(self):
        """Handle cookie banners by looking for 'Accept' or equivalent buttons."""
        try:
            self.page.click("button:has-text('Accept'), button:has-text('Allow'), button:has-text('Allow all'), button:has-text('I agree')", timeout=3000)
            time.sleep(1)
        except Exception:
            pass  # Ignore if no cookie button is found

    def search_files(self, query, engine="google"):
        """Perform a search and paginate through results to collect links."""
        search_urls = {
            "google": f"https://www.google.com/search?q={query}",
            "yandex": f"https://yandex.com/search/?text={query}",
            "duckduckgo": f"https://duckduckgo.com/?q={query}",
            "bing": f"https://www.bing.com/search?q={query}"
        }
        self.page.goto(search_urls[engine])
        self.accept_cookies()
        all_links = set()

        for _ in range(10):  # Limit to avoid infinite loops
            content = self.page.content()
            new_links = self.extract_links(content)
            all_links.update(new_links)

            if not self.go_to_next_page(engine):
                break  # Exit if no more pages

            time.sleep(2)  # Delay between pages

        return all_links

    def extract_links(self, content):
        """Extracts file links from the search engine content and filters by specified file types."""
        soup = BeautifulSoup(content, 'html.parser')
        links = set()
        for link in soup.find_all('a', href=True):
            url = link['href']
            if any(url.endswith(ext) for ext in self.file_types):
                full_url = urljoin(self.domain, url)
                if full_url not in self.seen_urls:
                    self.seen_urls.add(full_url)
                    links.add(full_url)
        return links

    def go_to_next_page(self, engine):
        """Navigate to the next page for each search engine."""
        try:
            if engine == "google":
                next_button = self.page.query_selector("a[aria-label='Next'], a:has-text('Next')")
            elif engine == "yandex":
                next_button = self.page.query_selector("a[aria-label='Next page'], a:has-text('Next')")
            elif engine == "bing":
                next_button = self.page.query_selector("a[title='Next page'], a[aria-label='Next page']")
            elif engine == "duckduckgo":
                next_button = self.page.query_selector("button:has-text('More results')")
            else:
                return False  # Unsupported engine

            if next_button:
                next_button.click()
                return True
            return False
        except Exception:
            return False

    def search_all_engines(self):
        """Performs searches across multiple search engines for each file type and collects unique links."""
        all_links = set()
        for file_type in self.file_types:
            query = f"filetype:{file_type} site:{self.domain}"
            for engine in ["google", "yandex", "duckduckgo", "bing"]:
                try:
                    print(f"Searching {engine} for .{file_type} files on {self.domain}")
                    links = self.search_files(query, engine)
                    all_links.update(links)
                except Exception as e:
                    print(f"Error searching on {engine}: {e}")
                time.sleep(2)
        return all_links

    def download_file(self, url):
        """Downloads a single file from the given URL."""
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            filename = os.path.basename(urlparse(url).path)
            filepath = os.path.join(self.output_dir, filename)
            with open(filepath, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Downloaded {filename}")
        else:
            print(f"Failed to download {url}")

    def download_files(self, links):
        """Downloads multiple files concurrently from the collected links."""
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.download_file, url) for url in links]
            for future in futures:
                future.result()

    def run(self):
        """Runs the entire search and download process."""
        self.start_browser()
        all_links = self.search_all_engines()
        self.close_browser()

        print(f"Downloading {len(all_links)} unique files.")
        self.download_files(all_links)
        
        print(f"Found {len(all_links)} unique files without downloading.")
        for link in all_links:
            print(link)
