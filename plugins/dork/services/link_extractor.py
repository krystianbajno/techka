from plugins.dork.extractors import GoogleExtractor, BingExtractor, DuckDuckGoExtractor, YandexExtractor, BaseExtractor

class LinkExtractor:
    @staticmethod
    def extract_links(content, engine, seen_urls):
        extractor: BaseExtractor = methods.get(engine, None)
        
        if not extractor:
            raise ValueError(f"Unknown search engine: {engine}")

        return extractor.extract_links(content, seen_urls)

methods = {
    "google": GoogleExtractor,
    "bing": BingExtractor,
    "duckduckgo": DuckDuckGoExtractor,
    "yandex": YandexExtractor
}