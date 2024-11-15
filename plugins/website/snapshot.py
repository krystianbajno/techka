import os
from urllib.parse import urljoin, urlparse
import requests
from playwright.sync_api import sync_playwright

SCRAPED_DIR = "data/output/scraped"

def handle_snapshot(url, output_file, auth_header=None):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    snapshot_dir = os.path.join(SCRAPED_DIR, f"{domain}-snapshot")
    os.makedirs(snapshot_dir, exist_ok=True)
    output_file_path = os.path.join(snapshot_dir, "index.html")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        if auth_header:
            key, value = auth_header.split("=", 1)
            page.set_extra_http_headers({key: value})

        try:
            page.goto(url, wait_until="networkidle")
            html_content = page.content()
            with open(output_file_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            print(f"Snapshot of {url} saved to {output_file_path}")

            assets = page.evaluate(
                """
                () => Array.from(document.querySelectorAll('link[rel="stylesheet"], script[src], img[src]'))
                          .map(el => el.href || el.src)
                """
            )
            for asset_url in assets:
                download_asset(asset_url, snapshot_dir, url)

        except Exception as e:
            print(f"Error fetching {url}: {e}")
        finally:
            browser.close()


def download_asset(asset_url, output_dir, base_url):
    try:
        parsed_asset_url = urlparse(asset_url)
        if not parsed_asset_url.netloc:
            asset_url = urljoin(base_url, asset_url)
        response = requests.get(asset_url, stream=True)
        response.raise_for_status()
        asset_path = os.path.join(output_dir, os.path.basename(parsed_asset_url.path))
        with open(asset_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"Downloaded asset: {asset_url} to {asset_path}")
    except requests.RequestException as e:
        print(f"Failed to download asset {asset_url}: {e}")
