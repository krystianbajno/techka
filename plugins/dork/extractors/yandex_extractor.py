from .base_extractor import BaseExtractor
from bs4 import BeautifulSoup

class YandexExtractor(BaseExtractor):
    @staticmethod
    def extract_links(content, seen_urls):
        soup = BeautifulSoup(content, 'html.parser')
        links_with_titles = {}

        for result in soup.find_all('div', class_='Organic'):
            title_tag = result.find('h2', class_='OrganicTitle-LinkText')
            link_tag = result.find('a', href=True)
            if title_tag and link_tag:
                title = title_tag.get_text(strip=True)
                url = link_tag['href']
                if url not in seen_urls:
                    links_with_titles[url] = title
                    seen_urls.add(url)

        return links_with_titles
