import os
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi

def download_video_with_audio(url: str, out_dir: str = ".", container_format: str = "mp4", audio_codec: str = "aac") -> None:
    opts = {
        "format": "bestvideo+bestaudio/best",
        "outtmpl": os.path.join(out_dir, "%(title)s", "%(title)s.%(ext)s"),
        "postprocessors": [{
            "key": "FFmpegVideoConvertor",
            "preferedformat": container_format
        }]
    }

    try:
        with yt_dlp.YoutubeDL(opts) as y:
            y.download([url])
        print(f"[INFO] Downloaded video+audio as {container_format} with audio codec {audio_codec}")
    except Exception as e:
        print(f"[ERROR] Video+audio download failed: {e}")

def download_audio(url: str, out_dir: str = ".", container_format: str = "wav") -> None:
    opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(out_dir, "%(title)s", "%(title)s.%(ext)s"),
        "postprocessors": [{
            "key": "FFmpegVideoConvertor",
            "preferedformat": container_format
        }]
    }

    try:
        with yt_dlp.YoutubeDL(opts) as y:
            y.download([url])
        print(f"[INFO] Downloaded audio as {container_format}")
    except Exception as e:
        print(f"[ERROR] Video+audio download failed: {e}")


def download_transcript(video_id: str, out_dir: str = ".", language: str = "en") -> None:
    try:
        tx = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
        lines = [f"{x['text']} ({x['start']}s)" for x in tx]
        fp = os.path.join(out_dir, f"{video_id}_transcript.txt")
        with open(fp, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"[INFO] Transcript saved at {fp}")
    except Exception as e:
        print(f"[ERROR] Transcript failed: {e}")


def download_description(url: str, out_dir: str = ".") -> None:
    try:
        opts = {"skip_download": True}
        with yt_dlp.YoutubeDL(opts) as y:
            info = y.extract_info(url, download=False)
            vid = info.get("id")
            desc = info.get("description", "")
            if not vid:
                print("[WARNING] Could not determine video ID for description.")
                return
            fp = os.path.join(out_dir, f"{vid}_description.txt")
            with open(fp, "w", encoding="utf-8") as f:
                f.write(desc)
        print("[INFO] Description downloaded.")
    except Exception as e:
        print(f"[ERROR] Description failed: {e}")
