import os
from concurrent.futures import ThreadPoolExecutor
from plugins.dork.services.browser_manager import BrowserManager
from plugins.dork.services.file_logger import FileLogger
from plugins.dork.services.downloader import Downloader
from plugins.dork.services.saver import deduplicate_links
from plugins.dork.services.search_runner import SearchRunner

class Dorking:
    def __init__(self, output_dir="output", max_pages=100, slow_search=False, link_file="collected_links.json", no_download=True):
        self.output_dir = output_dir
        self.max_pages = max_pages
        self.slow_search = slow_search
        self.link_file = link_file
        self.no_download = no_download
        self.seen_urls = set()
        self.logger = FileLogger(self.link_file)
        self.downloader = Downloader(self.output_dir, self.link_file)

        self.seen_urls = set(self.logger.load_links().keys())

    def run(self, query):
        if not self.no_download:
            print("Downloading content from collected links...")
            return self.downloader.download_collected_links()

        with ThreadPoolExecutor(max_workers=4) as executor:
            engines = {
                "google": f"https://www.google.com/search?q=",
                "bing": f"https://www.bing.com/search?q=",
                "duckduckgo": f"https://duckduckgo.com/?q=",
                "yandex": f"https://yandex.com/search/?text="
            }

            futures = []
            for engine_name, engine_url in engines.items():
                browser_manager = BrowserManager()
                search_runner = SearchRunner(browser_manager, self.logger, self.max_pages, self.slow_search)
                futures.append(executor.submit(search_runner.run_search, query, engine_name, engine_url, self.seen_urls))

            all_links = {}
            for future in futures:
                try:
                    result = future.result()
                    all_links.update(result)
                except Exception as e:
                    print(f"Error during concurrent search: {e}")

        print(f"Collected {len(all_links)} links.")

        existing_links = self.logger.load_links()
        unique_links = deduplicate_links(existing_links, all_links)

        self.logger.log_links(unique_links)

        print(f"Saved {len(unique_links)} unique links.")
