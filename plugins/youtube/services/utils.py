import re

def extract_video_id(url: str) -> str:
    """
    Extract the video ID from a YouTube URL.

    :param url: The YouTube video URL.
    :return: The extracted video ID or None if not found.
    """
    m = re.search(r"(?<=v=)[^&#]+", url)
    return m.group(0) if m else None
