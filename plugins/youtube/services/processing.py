import os
import yt_dlp

from .utils import extract_video_id
from .downloads import (
    download_audio,
    download_video_with_audio,
    download_transcript,
    download_description
)
from .comments import download_comments


def handle_single_video(
    url: str,
    out_dir: str = ".",
    do_video: bool = False,
    do_audio: bool = False,
    container_format: str = "mp4",
    audio_codec: str = "aac",
    do_transcript: bool = False,
    do_description: bool = False,
    do_comments: bool = False
) -> None:
    
    if "/shorts/" in url:
       url = url.replace('/shorts/', "/watch?v=")
    
    vid_id = extract_video_id(url)
    if not vid_id:
        print("[ERROR] Could not extract video ID.")
        return

    if do_video:
        download_video_with_audio(url, out_dir, container_format, audio_codec)
    if do_transcript:
        download_transcript(vid_id, out_dir)
    if do_description:
        download_description(url, out_dir)
    if do_comments:
        download_comments(url, out_dir)
    if do_audio:
        download_audio(url, out_dir)


def handle_channel(
    url: str,
    out_dir: str = ".",
    do_video: bool = False,
    container_format: str = "mp4",
    audio_codec: str = "aac",
    do_transcript: bool = False,
    do_description: bool = False,
    do_comments: bool = False
) -> None:
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    opts = {
        "extract_flat": "yes",
        "skip_download": True
    }
    try:
        with yt_dlp.YoutubeDL(opts) as y:
            info = y.extract_info(url, download=False)
            entries = info.get("entries", [])
            print(f"[INFO] Found {len(entries)} items in channel/playlist.")
            for e in entries:
                vid_url = e.get("url")
                if not vid_url:
                    continue
                handle_single_video(
                    url=vid_url,
                    out_dir=out_dir,
                    do_video=do_video,
                    container_format=container_format,
                    audio_codec=audio_codec,
                    do_transcript=do_transcript,
                    do_description=do_description,
                    do_comments=do_comments
                )
    except Exception as ex:
        print(f"[ERROR] Channel/playlist failed: {ex}")
