import sys
import argparse
import asyncio
from lib.api_keys import api_vault
from lib.log_utils import LogConfig, configure_logging, get_logger
from lib.paths import CachePaths, resolve_cache_paths
from lib.youtube_ids import YoutubeIdKind, extract_video_id
from lib.youtube_transcript import (
        youtube_json,
        youtube_text,
        youtube_paragraph
    )

# -----------------------------
# Logging setup
# -----------------------------
# configure_logging(LogConfig(level="DEBUG"), force=True)
configure_logging(LogConfig(level="INFO"))
logger = get_logger(__name__)

@dataclass(slots=True)  # , frozen=True)
class YouTubeSource:
    kind: YoutubeIdKind
    id: str
    url: str

def cache_url(yt_source: YouTubeSource)-> None:
    """ Cache the YouTube URL for future use. """
    cache_paths = resolve_cache_paths(
        app_name="aldale_yt_app",
        start=Path(__file__)
    )
    cache_file = cache_paths.app_cache_dir / yt_source.id+".url"
    try:
        with cache_file.open("w", encoding="utf-8") as f:
            f.write(yt_source.url + "\n")
        logger.info(f"Cached YouTube URL to {cache_file}")
    except Exception as e:
        logger.error(f"Failed to cache YouTube URL: {e}")


def get_url() -> YouTubeSource:
    """ Prompt the user for a YouTube URL and return a YouTubeSource. """
    while True:
        url = input("Enter YouTube URL: ").strip()
        if video_id := extract_video_id(url):
            return YouTubeSource(
                kind=YoutubeIdKind.VIDEO,
                id=video_id,
                url=url
            )
        else:
            print("Invalid YouTube URL or video ID. Please try again.")

def main():
    """ Main entry point: parse arguments and get desired transcript. """    
    parser = argparse.ArgumentParser(
        description="Get the transcript from a YouTube video in the desired format."
    )
    parser.add_argument("--output",
        choices=["json", "text", "paragraphs"],
        type=str.lower,
        default="json",
        help="Choose desired output."
    )
    parser.add_argument("--url", type=str, default="",
        help="YouTube URL to retreive the transcript from.")
    args = parser.parse_args()

    # 20251215 MMH Show help if no arguments are given
    if len(sys.argv) == 1:  
        parser.print_help()
        sys.exit(1)  # Exit with an error code

    video_id: str | None = None
    if not args.url or not (video_id := extract_video_id(args.url)):
        yt_source = get_url()
    else:
        yt_source = YouTubeSource(
            kind=YoutubeIdKind.VIDEO,
            id=video_id,
            url=args.url
        )

    cache_url(yt_source)

    match args.output:
        case "json":
            transcript = youtube_json(yt_source.id)
            print(transcript)
        case "text":
            transcript = youtube_text(yt_source.id)
            print(transcript)
        case "paragraphs":
            transcript = youtube_paragraph(yt_source.id)
            print(transcript)

if __name__ == "__main__":
    # If run as a script, execute main().
    main()
