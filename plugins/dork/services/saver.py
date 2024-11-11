import os
import json

def load_links_from_file(link_file):
    links = {}
    if os.path.exists(link_file):
        with open(link_file, 'r') as f:
            try:
                links = json.load(f)
            except json.JSONDecodeError:
                print(f"Error decoding JSON from {link_file}. Starting with an empty list.")
    return links

def deduplicate_links(existing_links, new_links):
    unique_links = existing_links.copy()
    for url, details in new_links.items():
        if url not in unique_links:
            unique_links[url] = details
    return unique_links

def save_unique_links(link_file, unique_links):
    with open(link_file, 'w') as f:
        json.dump(unique_links, f, indent=4)
