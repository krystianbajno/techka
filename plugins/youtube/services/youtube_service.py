import os
import re
from youtube_transcript_api import YouTubeTranscriptApi
import yt_dlp

def extract_video_id(url):
    video_id_match = re.search(r'(?<=v=)[^&#]+', url)
    return video_id_match.group(0) if video_id_match else None

def download_transcript(video_id, language='en', output_path="."):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
        transcript_text = "\n".join([f"{item['text']} ({item['start']}s)" for item in transcript])
        transcript_path = os.path.join(output_path, f"{video_id}_transcript.txt")
        with open(transcript_path, "w") as file:
            file.write(transcript_text)
        print(f"Transcript downloaded and saved as {transcript_path}")
    except Exception as e:
        print(f"Could not download transcript for video ID {video_id}: {e}")

def download_video(video_url, output_path="."):
    try:
        ydl_opts = {
            'format': 'best',
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s')
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        print(f"Video downloaded successfully: {video_url}")
    except Exception as e:
        print(f"Could not download video: {e}")

def download_audio(video_url, output_path=".", audio_format="mp3"):
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': audio_format,
                'preferredquality': '192',
            }],
            'postprocessor_args': [
                '-ar', '16000'
            ],
            'prefer_ffmpeg': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        print(f"Audio downloaded successfully: {video_url}")
    except Exception as e:
        print(f"Could not download audio: {e}")

def download_youtube_content(url, output_path="."):
    video_id = extract_video_id(url)
    if not video_id:
        print("Invalid URL. Please provide a valid YouTube video URL.")
        return

    print("Downloading transcript...")
    download_transcript(video_id, output_path=output_path)
    print("Downloading video...")
    download_video(url, output_path)

def download_channel_content(channel_url, output_path="."):
    try:
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        ydl_opts = {
            'extract_flat': 'yes',
            'skip_download': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(channel_url, download=False)
            video_urls = [entry['url'] for entry in info['entries']]
            print(f"Found {len(video_urls)} videos in the channel.")

        for video_url in video_urls:
            print(f"\nProcessing video: {video_url}")
            download_video(video_url, output_path)

            video_id = extract_video_id(video_url)
            if video_id:
                download_transcript(video_id, output_path=output_path)
            else:
                print(f"Failed to extract video ID from URL: {video_url}")

    except Exception as e:
        print(f"Error accessing channel or downloading content: {e}")
