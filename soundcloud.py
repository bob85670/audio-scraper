"""Search SoundCloud playlists for audio."""

import json
import logging
import os
import string
import sys

import requests
from sclib import SoundcloudAPI, Track
from tqdm import tqdm

logger = logging.getLogger(__name__)


def sanitize(s):
    valid = f"-_.() {string.ascii_letters}{string.digits}"
    return "".join(c for c in s if c in valid)


if "SOUNDCLOUD_API_KEY" in os.environ:
    API_KEY = os.environ["SOUNDCLOUD_API_KEY"]
else:
    API_KEY = "81f430860ad96d8170e3bf1639d4e072"


def scrape(query):
    """
    Search SoundCloud and download the first track from the first playlist found for the query.
    """
    logger.info("[soundcloud] Starting scrape with api")
    directory = "audio_data"
    os.makedirs(directory, exist_ok=True)
    client = SoundcloudAPI()

    # Step 1: Search for playlists using SoundCloud search page
    search_url = f"https://soundcloud.com/search/sets?q={requests.utils.quote(query)}"
    resp = requests.get(search_url)
    logger.info("[soundcloud] Fetching search results")
    if not resp.ok:
        logger.error(f"Failed to fetch search results for query: {query}")
        return

    # Step 2: Find playlist URLs in search results (look for '/{user}/sets/{playlist-name}')
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(resp.text, "html.parser")
    playlist_url = None
    for link in soup.find_all("a", href=True):
        href = link["href"]
        if href.startswith("/") and "/sets/" in href:
            playlist_url = "https://soundcloud.com" + href
            break
    if not playlist_url:
        logger.warning("No playlists found for query: %s", query)
        return

    # Step 3: Process only the first playlist and download first track
    try:
        playlist = client.resolve(playlist_url)
    except Exception as e:
        logger.warning(f"Could not resolve: {playlist_url} ({e})")
        return

    logger.info(f"Downloading from playlist: {playlist.title}")
    tracks = list(playlist.tracks)
    if tracks:
        track = tracks[0]
        file = os.path.join("audio_data", sanitize(track.title) + ".mp3")
        # Skip if file exists
        if os.path.exists(file):
            logger.info(f"Track already exists: {file}")
            return
        # Skip tracks that cannot be streamed
        if not getattr(track, "streamable", True):
            logger.info("Track is not streamable.")
            return
        # Download track
        r = requests.get(track.get_stream_url(), stream=True)
        total_size = int(r.headers.get("content-length", 0))
        chunk_size = 1000000  # 1 MB chunks
        with open(file, "wb") as f:
            for data in tqdm(
                r.iter_content(chunk_size),
                desc=track.title,
                total=total_size / chunk_size if total_size else None,
                unit="MB",
                file=sys.stdout,
            ):
                f.write(data)
        logger.info(f"Finished downloading track: {file}")
