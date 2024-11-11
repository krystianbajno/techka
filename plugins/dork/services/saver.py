import os


def load_links_from_file(link_file):
    links = {}
    if os.path.exists(link_file):
        with open(link_file, 'r') as f:
            for line in f:
                url, title = line.strip().split('\t', 1)
                links[url] = title
    return links

def deduplicate_links(existing_links, new_links):
    unique_links = existing_links.copy()
    for url, title in new_links.items():
        if url not in unique_links:
            unique_links[url] = title
    return unique_links

def save_unique_links(link_file, unique_links):
    with open(link_file, 'w') as f:
        for url, title in unique_links.items():
            f.write(f"{url}\t{title}\n")
