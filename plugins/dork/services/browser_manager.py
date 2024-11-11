from playwright.sync_api import sync_playwright

class BrowserManager:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None

    def start_browser(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=False)
        self.page = self.browser.new_page()

    def close_browser(self):
        try:
            if self.page:
                self.page.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
        except:
            print("Browser was closed by the user or encountered an error.")

    def goto_page(self, url):
        self.page.goto(url)

    def get_page_content(self):
        return self.page.content()

    def is_browser_open(self):
        try:
            self.page.title()
            return True
        except:
            return False
