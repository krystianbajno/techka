import os
import json

class FileLogger:
    def __init__(self, link_file):
        self.link_file = link_file

    def log_links(self, links):
        os.makedirs(os.path.dirname(self.link_file), exist_ok=True)

        existing_links = self.load_links()

        existing_links.update(links)

        with open(self.link_file, 'w', encoding='utf-8') as f:
            json.dump(existing_links, f, ensure_ascii=False, indent=4)

    def load_links(self):
        if os.path.exists(self.link_file):
            with open(self.link_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
