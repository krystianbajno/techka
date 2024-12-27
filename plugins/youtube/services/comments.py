import os
import re
import time
import json

try:
    from playwright.sync_api import sync_playwright, Page
except ImportError:
    sync_playwright = None

def extract_video_id(url: str) -> str:
    match = re.search(r"(?:v=)([a-zA-Z0-9_\-]{11})", url)
    if match:
        return match.group(1)
    return ""

def accept_cookies(page: "Page") -> None:
    try:
        page.click("button:has-text('Accept all')", timeout=3000)
    except:
        pass

def remove_related_section(page: "Page") -> None:
    page.evaluate("""
    const selList = [
      '#related',
      '#secondary'
    ];
    selList.forEach(sel => {
      const el = document.querySelector(sel);
      if (el) el.remove();
    });
    """)

def is_view_replies_button(text: str) -> bool:
    text_lower = text.strip().lower()

    if text_lower == "reply":
        return False

    if re.match(r"^\d+\s+repl(y|ies)$", text_lower):
        return True

    if text_lower.startswith("view") and "reply" in text_lower:
        return True

    return False

def get_button_key(btn) -> str:
    try:
        txt = (btn.inner_text() or "").strip()
        html = btn.evaluate("el => el.outerHTML")
        return f"{txt}__{html}"
    except:
        return str(btn)
    
def expand_replies(page: "Page", clicked_buttons: set) -> int:
    newly_clicked = 0
    all_buttons = page.query_selector_all("button")
    for btn in all_buttons:
        text = (btn.inner_text() or "").strip()
        if not is_view_replies_button(text):
            continue

        key = get_button_key(btn)
        if key not in clicked_buttons:
            try:
                btn.click()
                time.sleep(0.8)
                clicked_buttons.add(key)
                newly_clicked += 1
            except:
                pass
    return newly_clicked

def expand_top_level_comments(page: "Page", clicked_buttons: set) -> int:
    newly_clicked = 0
    for text_option in ["Show more", "Load more"]:
        selector = f"tp-yt-paper-button:has-text('{text_option}')"
        btn_list = page.query_selector_all(selector)
        for btn in btn_list:
            key = get_button_key(btn)
            if key not in clicked_buttons:
                try:
                    btn.click()
                    time.sleep(0.8)
                    clicked_buttons.add(key)
                    newly_clicked += 1
                except:
                    pass
    return newly_clicked

def scroll_page(page: "Page"):
    for _ in range(3):
        page.mouse.wheel(0, 3000)
        time.sleep(1.5)

def gather_comments_data(page: "Page") -> list:
    data = []
    
    thread_list = page.query_selector_all("ytd-comment-thread-renderer")
    
    for thread in thread_list:
        top_comment_el = thread.query_selector("#comment")
        if not top_comment_el:
            continue
    
        auth_el = top_comment_el.query_selector("#author-text")
        author = auth_el.inner_text().strip() if auth_el else ""
        
        txt_el = top_comment_el.query_selector("#content #content-text")
        text = txt_el.inner_text().strip() if txt_el else ""
        
        likes_el = top_comment_el.query_selector("#vote-count-middle")
        likes = (likes_el.inner_text().strip() if likes_el else "0") or "0"
        
        link_el = top_comment_el.query_selector("#author-text a")
        profile_url = link_el.get_attribute("href") if link_el else ""
        if profile_url.startswith("/"):
            profile_url = "https://www.youtube.com" + profile_url
        
        replies_block = thread.query_selector("#replies")
        replies_data = []
        
        if replies_block:
            reply_elems = replies_block.query_selector_all("#comment")
            for r in reply_elems:
                print(r.text_content())
                ra_el = r.query_selector("#author-text")
                ra = ra_el.inner_text().strip() if ra_el else ""
                
                rt_el = r.query_selector("#content #content-text")
                rt = rt_el.inner_text().strip() if rt_el else ""
                
                rl_el = r.query_selector("#vote-count-middle")
                rl = (rl_el.inner_text().strip() if rl_el else "0") or "0"
                
                rlink_el = r.query_selector("#author-text a")
                rprof = rlink_el.get_attribute("href") if rlink_el else ""
                if rprof.startswith("/"):
                    rprof = "https://www.youtube.com" + rprof
                
                replies_data.append({
                    "author": ra,
                    "text": rt,
                    "likes": rl,
                    "profile_url": rprof
                })
        
        data.append({
            "author": author,
            "text": text,
            "likes": likes,
            "profile_url": profile_url,
            "replies": replies_data
        })
    
    return data


def scrape_all_comments(page: "Page") -> list:
    page.wait_for_selector("#comments", timeout=20000)

    clicked_buttons = set()
    last_count = 0
    stable_rounds = 0
    max_stable = 4

    while True:
        remove_related_section(page)

        found_replies = expand_replies(page, clicked_buttons)

        found_top = expand_top_level_comments(page, clicked_buttons)

        scroll_page(page)

        thread_count = len(page.query_selector_all("ytd-comment-thread-renderer"))

        if thread_count == last_count:
            stable_rounds += 1
        else:
            stable_rounds = 0
            last_count = thread_count

        no_new_clicks = (found_replies == 0 and found_top == 0)
        if stable_rounds >= max_stable and no_new_clicks:
            break

    data = gather_comments_data(page)
    return data

def download_comments(url: str, out_dir: str = ".") -> None:
    if not sync_playwright:
        print("[ERROR] You must install playwright to run this script.")
        return

    video_id = extract_video_id(url)
    if not video_id:
        print("[ERROR] Could not extract video ID from URL.")
        return

    fp = os.path.join(out_dir, f"{video_id}_comments.json")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()

            page.set_default_navigation_timeout(60000)
            page.set_default_timeout(60000)

            page.goto(url, wait_until="networkidle")
            page.wait_for_load_state("networkidle")

            accept_cookies(page)
            time.sleep(1)

            comments_data = scrape_all_comments(page)

            browser.close()

        with open(fp, "w", encoding="utf-8") as f:
            json.dump(comments_data, f, indent=2, ensure_ascii=False)
        print(f"[INFO] Comments saved to: {fp}")

    except Exception as e:
        print(f"[ERROR] Could not scrape comments: {e}")
