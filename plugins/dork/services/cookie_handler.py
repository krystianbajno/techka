class CookieHandler:
    @staticmethod
    def accept_cookies(browser_manager):
        try:
            browser_manager.page.click(
                "button:has-text('Accept'), button:has-text('Allow'), button:has-text('I agree'), "
                "button:has-text('Got it'), button:has-text('Yes'), button:has-text('OK')",
                timeout=5000
            )
            print("Cookies accepted.")
        except Exception:
            print("No cookies prompt found or failed to accept cookies.")
