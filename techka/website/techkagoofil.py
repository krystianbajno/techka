import os
import mimetypes
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import requests

class TechkaGoofil:
    def __init__(self, domain, output_dir="output", file_types=None, max_pages=200, slow_download=False, link_file="discovered_links.txt"):
        self.domain = domain
        self.output_dir = output_dir
        self.file_types = file_types or ["pdf", "docx", "doc", "txt"]
        self.max_pages = int(max_pages) if max_pages else 200
        self.slow_download = slow_download
        self.link_file = link_file
        self.seen_urls = set()
        self.file_metadata = {}
        self.links_loaded_from_file = False
        os.makedirs(self.output_dir, exist_ok=True)

        if os.path.exists(self.link_file):
            self._load_links_from_file()

    def _load_links_from_file(self):
        choice = input(f"{self.link_file} exists. Download files now without further TechkaGoofil search? (y/n): ")
        if choice.lower() == 'y':
            with open(self.link_file, 'r') as f:
                for line in f:
                    url, title = line.strip().split('\t', 1)
                    if url not in self.seen_urls:
                        self.file_metadata[url] = title
                        self.seen_urls.add(url)
            self.links_loaded_from_file = True

    def start_browser(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=False)
        self.page = self.browser.new_page()

    def close_browser(self):
        self.page.close()
        self.browser.close()
        self.playwright.stop()

    def _search_files_on_engine(self, query, engine_url, engine_name):
        self.page.goto(engine_url)
        self.accept_cookies()
        all_links = set()

        try:
            for _ in range(self.max_pages):
                content = self.page.content()
                new_links = self.extract_links_with_titles(content, engine_name)
                all_links.update(new_links)
                if not self.go_to_next_page(engine_url):
                    break
                time.sleep(1)
        except Exception as e:
            print(f"Search error on {engine_url} for query '{query}': {e}")

        return all_links

    def accept_cookies(self):
        try:
            self.page.click("button:has-text('Accept'), button:has-text('Allow'), button:has-text('Allow all'), button:has-text('I agree')", timeout=3000)
            time.sleep(1)
        except Exception:
            pass

    def extract_links_with_titles(self, content, engine):
        soup = BeautifulSoup(content, 'html.parser')
        links_with_titles = {}

        if engine == "google":
            for result in soup.find_all('div', class_='g'):
                title_tag = result.find('h3')
                link_tag = result.find('a', href=True)
                if title_tag and link_tag:
                    title = title_tag.get_text(strip=True)
                    url = link_tag['href']
                    if url not in self.seen_urls:
                        links_with_titles[url] = title
                        self.seen_urls.add(url)

        elif engine == "duckduckgo":
            for result in soup.find_all('article', {'data-testid': 'result'}):
                title_tag = result.find('h2')
                link_tag = title_tag.find('a', href=True) if title_tag else None
                if title_tag and link_tag:
                    title = title_tag.get_text(strip=True)
                    url = link_tag['href']
                    if url not in self.seen_urls:
                        links_with_titles[url] = title
                        self.seen_urls.add(url)

        elif engine == "bing":
            for result in soup.find_all('li', class_='b_algo'):
                title_tag = result.find('h2')
                link_tag = title_tag.find('a', href=True) if title_tag else None
                if title_tag and link_tag:
                    title = title_tag.get_text(strip=True)
                    url = link_tag['href']
                    if url not in self.seen_urls:
                        links_with_titles[url] = title
                        self.seen_urls.add(url)

        elif engine == "yandex":
            for result in soup.find_all('div', class_='Organic'):
                title_tag = result.find('h2', class_='OrganicTitle-LinkText')
                link_tag = result.find('a', href=True)
                if title_tag and link_tag:
                    title = title_tag.get_text(strip=True)
                    url = link_tag['href']
                    if url not in self.seen_urls:
                        links_with_titles[url] = title
                        self.seen_urls.add(url)

        self.file_metadata.update(links_with_titles)
        with open(self.link_file, "a") as f:
            for url, title in links_with_titles.items():
                f.write(f"{url}\t{title}\n")

        return links_with_titles.keys()
    
    def _log_links_to_file(self, links):
        with open(self.link_file, "a") as f:
            for url, title in links.items():
                f.write(f"{url}\t{title}\n")

    def go_to_next_page(self, engine):
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
                return False

            if next_button:
                next_button.click()
                return True
            return False
        except Exception as e:
            print(f"Failed to navigate to the next page on {engine}: {e}")
            return False

    def search_all_engines(self):
        all_links = set()
        for file_type in self.file_types:
            query = f"filetype:{file_type} site:{self.domain}"
            for engine_name, engine_url in {
                "google": f"https://www.google.com/search?q={query}",
                "yandex": f"https://yandex.com/search/?text={query}",
                "duckduckgo": f"https://duckduckgo.com/?q={query}",
                "bing": f"https://www.bing.com/search?q={query}"
            }.items():
                try:
                    print(f"Searching {engine_name} for .{file_type} files on {self.domain}")
                    links = self._search_files_on_engine(query, engine_url, engine_name)
                    all_links.update(links)
                except Exception as e:
                    print(f"Search error on {engine_name}: {e}")
                time.sleep(2)
        return all_links

    def download_file(self, url, title):
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            content_type = response.headers.get('Content-Type', '').split(';')[0]
            filename = f"{title}.{mimetypes.guess_extension(content_type) or 'bin'}"
            filepath = os.path.join(self.output_dir, filename)

            with open(filepath, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    if self.slow_download:
                        time.sleep(0.1)
            print(f"Downloaded {filename}")
        except Exception as e:
            print(f"Download error for {url}: {e}")

    def download_files(self):
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.download_file, url, title) for url, title in self.file_metadata.items()]
            for future in as_completed(futures):
                future.result()

    def run(self):
        if not self.links_loaded_from_file:
            self.start_browser()
            self.search_all_engines()
            self.close_browser()
            print(f"Downloading {len(self.file_metadata)} unique files.")
        else:
            print(f"Using {len(self.file_metadata)} preloaded links for downloading.")

        self.download_files()
        return self.seen_urls, self.file_metadata
