from .base_extractor import BaseExtractor
from bs4 import BeautifulSoup

class GoogleExtractor(BaseExtractor):
    @staticmethod
    def extract_links(content, seen_urls):
        soup = BeautifulSoup(content, 'html.parser')
        links_with_details = {}

        for result in soup.find_all('div'):
            title_tag = result.find('h3')
            if title_tag:
                title = title_tag.get_text(strip=True)
            else:
                continue

            link_tag = result.find('a', href=True)
            if link_tag:
                url = link_tag['href']
            else:
                continue

            description = result.get_text(strip=True)

            if url not in seen_urls:
                links_with_details[url] = {
                    'title': title,
                    'description': description
                }
                seen_urls.add(url)

        return links_with_details
