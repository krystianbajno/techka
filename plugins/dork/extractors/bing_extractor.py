from .base_extractor import BaseExtractor
from bs4 import BeautifulSoup

class BingExtractor(BaseExtractor):
    @staticmethod
    def extract_links(content, seen_urls):
        soup = BeautifulSoup(content, 'html.parser')
        links_with_titles = {}

        for result in soup.find_all('li', class_='b_algo'):
            title_tag = result.find('h2')
            link_tag = title_tag.find('a', href=True) if title_tag else None
            if title_tag and link_tag:
                title = title_tag.get_text(strip=True)
                url = link_tag['href']
                if url not in seen_urls:
                    links_with_titles[url] = title
                    seen_urls.add(url)

        return links_with_titles
