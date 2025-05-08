"""Rip audio from YouTube videos."""

import logging
import re
from urllib.parse import urlencode
from urllib.request import urlopen

import yt_dlp as yt

logger = logging.getLogger(__name__)


def scrape(query):
    """Search YouTube and download audio from the first discovered video."""
    import os
    os.makedirs("audio_data", exist_ok=True)

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
        "outtmpl": "audio_data/%(title)s.%(ext)s",
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
