import time

class NavigationHandler:
    @staticmethod
    def navigate_to_next_page(browser_manager, engine):
        try:
            page = browser_manager.page

            next_button_selectors = {
                "google": "a[aria-label='Next'], a:has-text('Next')",
                "bing": "a[title='Next page'], a[aria-label='Next page']",
                "duckduckgo": "button:has-text('More results')",
                "yandex": "a[aria-label='Next page'], a:has-text('Next')"
            }

            selector = next_button_selectors.get(engine)
            if selector:
                next_button = page.query_selector(selector)
                if next_button:
                    next_button.click()
                    time.sleep(1)
                    return True
            return False
        except Exception as e:
            print(f"Failed to navigate to the next page on {engine}: {e}")
            return False
