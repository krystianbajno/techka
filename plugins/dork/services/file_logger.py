import os

class FileLogger:
    def __init__(self, link_file):
        self.link_file = link_file

    def log_links(self, links):
        with open(self.link_file, "a") as f:
            for url, title in links.items():
                f.write(f"{url}\t{title}\n")

    def load_links(self, seen_urls, file_metadata):
        if os.path.exists(self.link_file):
            with open(self.link_file, 'r') as f:
                for line in f:
                    url, title = line.strip().split('\t', 1)
                    if url not in seen_urls:
                        file_metadata[url] = title
                        seen_urls.add(url)
            print(f"Loaded {len(seen_urls)} URLs from {self.link_file}.")
