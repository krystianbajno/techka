from bs4 import BeautifulSoup

class BaseExtractor:
    @staticmethod
    def extract_links(content, seen_urls):
        raise NotImplementedError("This method should be implemented in a subclass.")
