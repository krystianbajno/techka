from plugins.plugin_base import Plugin
from plugins.youtube.services.processing import handle_single_video, handle_channel

output_path = "data/youtube/"

class Handler(Plugin):
    def register_as(self):
        return "youtube"

    def commands(self, subparsers):
        parser = subparsers.add_parser(self.register_as(), help="YouTube commands")
        sp = parser.add_subparsers(dest="mode", required=True)

        single_parser = sp.add_parser("single", help="Process single video")
        single_parser.add_argument("url", type=str)
        single_parser.add_argument("--output-path", type=str, default=".")
        single_parser.add_argument("--video", action="store_true")
        single_parser.add_argument("--audio", action="store_true")
        single_parser.add_argument("--transcript", action="store_true")
        single_parser.add_argument("--description", action="store_true")
        single_parser.add_argument("--comments", action="store_true")
        single_parser.add_argument("--container-format", type=str, default="mp4", 
                                   help="Output container (e.g. mp4, mkv)")
        single_parser.add_argument("--audio-codec", type=str, default="aac",
                                   help="Audio codec (e.g. aac, pcm_s16le)")

        channel_parser = sp.add_parser("channel", help="Process entire channel/playlist")
        channel_parser.add_argument("url", type=str)
        channel_parser.add_argument("--output-path", type=str, default=".")
        channel_parser.add_argument("--video", action="store_true")
        channel_parser.add_argument("--audio", action="store_true")
        channel_parser.add_argument("--transcript", action="store_true")
        channel_parser.add_argument("--description", action="store_true")
        channel_parser.add_argument("--comments", action="store_true")
        channel_parser.add_argument("--container-format", type=str, default="mp4")
        channel_parser.add_argument("--audio-codec", type=str, default="aac")

    def handle(self, args):
        if args.mode == "single":
            handle_single_video(
                url=args.url,
                out_dir=output_path,
                do_video=args.video,
                do_audio=args.audio,
                container_format=args.container_format,
                audio_codec=args.audio_codec,
                do_transcript=args.transcript,
                do_description=args.description,
                do_comments=args.comments
            )
        elif args.mode == "channel":
            handle_channel(
                url=args.url,
                out_dir=output_path,
                do_video=args.video,
                container_format=args.container_format,
                audio_codec=args.audio_codec,
                do_transcript=args.transcript,
                do_description=args.description,
                do_comments=args.comments
            )
