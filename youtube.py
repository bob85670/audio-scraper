"""Rip audio from YouTube videos."""

import logging
import re
from urllib.parse import urlencode
from urllib.request import urlopen

import yt_dlp as yt

logger = logging.getLogger(__name__)


def scrape(query, output_dir=None):
    """Search YouTube and download audio from the first discovered video.

    Args:
        query (str): The YouTube search query.
        output_dir (str or None): Directory where to save the mp3.
            If None (default), saves in 'audio_data'. If '', saves in current dir.
    """
    import os

    if output_dir is None:
        output_dir = "audio_data"
        os.makedirs(output_dir, exist_ok=True)
        outtmpl = os.path.join(output_dir, "%(title)s.%(ext)s")
    else:
        outtmpl = "%(title)s.%(ext)s" if output_dir == "" else os.path.join(output_dir, "%(title)s.%(ext)s")
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

    # Search YouTube for videos.
    query_string = urlencode({"search_query": query})
    url = f"http://youtube.com/results?{query_string}"

    with urlopen(url) as response:
        html = response.read().decode("utf-8")
        logger.debug(html)

    video_ids = re.findall(r"\"\/watch\?v=(.{11})", html)
    if not video_ids:
        logger.warning("No videos found for query: %s", query)
        return

    # Only download the first video
    video_id = video_ids[0]
    logger.info(f"Getting video: {video_id}")
    video_url = f"https://www.youtube.com/watch?v={video_id}"

    download_options = {
        "format": "bestaudio/best",
        "outtmpl": outtmpl,
        "writeinfojson": False,
        "writethumbnail": False,
        "writedescription": False,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }
    ydl = yt.YoutubeDL(download_options)
    video_info = ydl.extract_info(video_url, download=False)
    logger.debug(video_info)
    ydl.download([video_url])
    
if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="Download audio from YouTube for a single song query."
    )
    parser.add_argument(
        "query",
        type=str,
        help="Song query to search and download from YouTube (e.g., 'Miley Cyrus Flowers')"
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(message)s")

    try:
        scrape(args.query, output_dir="")
        print("Done.")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
