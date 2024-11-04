from plugins.plugin_base import Plugin
from plugins.youtube.services.youtube_service import (
    download_transcript,
    download_video,
    download_youtube_content,
    download_channel_content,
    extract_video_id
)

class Handler(Plugin):
    def register_as(self):
        return "youtube"

    def commands(self, subparsers):
        youtube_parser = subparsers.add_parser(self.register_as(), help="YouTube related commands")
        youtube_subparsers = youtube_parser.add_subparsers(dest="action", required=True)

        youtube_transcript_parser = youtube_subparsers.add_parser("transcript", help="Download YouTube video transcript")
        youtube_transcript_parser.add_argument("url", type=str, help="URL of the YouTube video to download")
        youtube_transcript_parser.add_argument("--language", type=str, default="en", help="Language for the transcript")

        youtube_video_parser = youtube_subparsers.add_parser("video", help="Download YouTube video")
        youtube_video_parser.add_argument("url", type=str, help="URL of the YouTube video to download")
        youtube_video_parser.add_argument("--output-path", type=str, default=".", help="Directory to save the downloaded video")

        youtube_both_parser = youtube_subparsers.add_parser("both", help="Download both video and transcript")
        youtube_both_parser.add_argument("url", type=str, help="URL of the YouTube video to download")
        youtube_both_parser.add_argument("--language", type=str, default="en", help="Language for the transcript")
        youtube_both_parser.add_argument("--output-path", type=str, default=".", help="Directory to save the downloaded video and transcript")

        youtube_channel_parser = youtube_subparsers.add_parser("channel", help="Download all videos and transcripts from a YouTube channel")
        youtube_channel_parser.add_argument("url", type=str, help="URL of the YouTube channel")
        youtube_channel_parser.add_argument("--language", type=str, default="en", help="Language for the transcripts")
        youtube_channel_parser.add_argument("--output-path", type=str, default=".", help="Directory to save the downloaded videos and transcripts")

    def handle(self, args):
        action_map = {
            "transcript": self._download_transcript,
            "video": self._download_video,
            "both": self._download_both,
            "channel": self._download_channel,
        }

        action = args.action
        if action in action_map:
            action_map[action](args)

    def _download_transcript(self, args):
        language = args.language
        try:
            video_id = extract_video_id(args.url)
            download_transcript(video_id, language)
            print(f"Transcript downloaded successfully and saved as {video_id}_transcript.txt")
        except Exception as e:
            print(f"Error downloading transcript: {e}")

    def _download_video(self, args):
        try:
            download_video(args.url, args.output_path)
            print(f"Video downloaded successfully from {args.url}")
        except Exception as e:
            print(f"Error downloading video: {e}")

    def _download_both(self, args):
        try:
            download_youtube_content(args.url, args.output_path)
        except Exception as e:
            print(f"Error downloading content: {e}")

    def _download_channel(self, args):
        try:
            download_channel_content(args.url, args.output_path)
        except Exception as e:
            print(f"Error downloading channel content: {e}")
