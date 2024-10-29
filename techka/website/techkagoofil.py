import mimetypes
import os
import time
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import requests

class TechkaGoofil:
    def __init__(self, domain, output_dir="output", file_types=["pdf", "docx", "doc", "txt"], max_pages=100):
        self.domain = domain
        self.output_dir = output_dir
        self.file_types = file_types
        self.seen_urls = set()
        self.max_pages = max_pages
        os.makedirs(self.output_dir, exist_ok=True)
        self.file_metadata = {}

    def start_browser(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=False)
        self.page = self.browser.new_page()

    def close_browser(self):
        self.browser.close()
        self.playwright.stop()

    def accept_cookies(self):
        try:
            self.page.click("button:has-text('Accept'), button:has-text('Allow'), button:has-text('Allow all'), button:has-text('I agree')", timeout=3000)
            time.sleep(1)
        except Exception:
            pass

    def search_files(self, query, engine="google"):
        search_urls = {
            "google": f"https://www.google.com/search?q={query}",
            "yandex": f"https://yandex.com/search/?text={query}",
            "duckduckgo": f"https://duckduckgo.com/?q={query}",
            "bing": f"https://www.bing.com/search?q={query}"
        }
        self.page.goto(search_urls[engine])
        self.accept_cookies()
        all_links = set()

        for _ in range(self.max_pages):
            content = self.page.content()
            new_links = self.extract_links_with_titles(content, engine)
            all_links.update(new_links)

            if not self.go_to_next_page(engine):
                break

            time.sleep(1)

        return all_links

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
                    links_with_titles[url] = title

        elif engine == "duckduckgo":
            for result in soup.find_all('article', {'data-testid': 'result'}):
                title_tag = result.find('h2')
                link_tag = title_tag.find('a', href=True) if title_tag else None
                if title_tag and link_tag:
                    title = title_tag.get_text(strip=True)
                    url = link_tag['href']
                    links_with_titles[url] = title

        elif engine == "bing":
            for result in soup.find_all('li', class_='b_algo'):
                title_tag = result.find('h2')
                link_tag = title_tag.find('a', href=True) if title_tag else None
                if title_tag and link_tag:
                    title = title_tag.get_text(strip=True)
                    url = link_tag['href']
                    links_with_titles[url] = title

        elif engine == "yandex":
            for result in soup.find_all('div', class_='Organic'):
                title_tag = result.find('h2', class_='OrganicTitle-LinkText')
                link_tag = result.find('a', href=True)
                if title_tag and link_tag:
                    title = title_tag.get_text(strip=True)
                    url = link_tag['href']
                    links_with_titles[url] = title

        self.file_metadata.update(links_with_titles)
        return links_with_titles.keys()

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
        except Exception:
            return False

    def search_all_engines(self):
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

    def download_file(self, url, title):
        try:
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                filename = f"{title}.{mimetypes.guess_extension(response.headers.get('Content-Type', '').split(';')[0]) or 'bin'}"
                filepath = os.path.join(self.output_dir, filename)
                
                with open(filepath, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"Downloaded {filename}")
            else:
                print(f"Failed to download {url}")
        except Exception as e:
            print(f"Failed to download {url}: {e}")

    def download_files(self, links):
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.download_file, url, title) for url, title in self.file_metadata.items()]
            for future in futures:
                future.result()

    def run(self):
        self.start_browser()
        all_links = self.search_all_engines()
        self.close_browser()

        print(f"Downloading {len(all_links)} unique files.")
        
        self.download_files(all_links)
                
        return all_links, self.file_metadata
