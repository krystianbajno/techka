import time
from plugins.dork.services.link_extractor import LinkExtractor
from plugins.dork.services.navigation import NavigationHandler
from plugins.dork.services.cookie_handler import CookieHandler

class SearchRunner:
    def __init__(self, browser_manager, logger, max_pages, slow_search):
        self.browser_manager = browser_manager
        self.logger = logger
        self.max_pages = max_pages
        self.slow_search = slow_search

    def run_search(self, query, engine_name, engine_url, seen_urls):
        try:
            self.browser_manager.start_browser()
            search_url = engine_url + query
            self.browser_manager.goto_page(search_url)

            CookieHandler.accept_cookies(self.browser_manager)

            all_links = {}

            for page_number in range(self.max_pages):
                if not self.browser_manager.is_browser_open():
                    print(f"User closed the browser. Saving results for {engine_name}.")
                    self.logger.log_links(all_links)
                    break

                content = self.browser_manager.get_page_content()
                new_links = LinkExtractor.extract_links(content, engine_name, seen_urls)
                all_links.update(new_links)

                self.logger.log_links(all_links)

                for attempt in range(3):
                    if NavigationHandler.navigate_to_next_page(self.browser_manager, engine_name):
                        print(f"Navigated to page {page_number + 2} on {engine_name}")
                        if self.slow_search:
                            time.sleep(2)
                        break
                    else:
                        print(f"Retrying navigation attempt {attempt + 1} on {engine_name}...")
                        time.sleep(1)

                else:
                    print(f"Reached the end of results or failed to navigate further on {engine_name}.")
                    break

            return all_links
        except Exception as e:
            print(f"Error during search on {engine_name}: {e}")
        finally:
            self.browser_manager.close_browser()
